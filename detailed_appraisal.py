""" 
UI widget for detailed appraisals performed by Triton FAS

Angus Toms
12 05 2021
"""
import json
import os
from functools import partial
from typing import List, Tuple

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QFileDialog, QFormLayout, QGridLayout,
                             QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QRadioButton,
                             QScrollArea, QSpinBox, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout,
                             QWidget)

import const
import utils
from detailed_datahandler import DetailedDataHandler

"""
####################
######## MAIN ######
####################
"""


class DetailedAppraisal(QWidget):
    """_summary_

    Args:
        QWidget (_type_): _description_
    """
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

        # Display fields
        self.tabs = QTabWidget()

        self.db = DetailedDataHandler()

        self.upload_tab = UploadTab(self, self.db)
        self.res_tab = ResidentialTab(self, self.db)
        self.non_res_tab = NonResidentialTab(self, self.db)
        self.ascii_tab = AsciiTab(self, self.db)
        self.node_tab = NodeTab(self, self.db)
        self.results_tab = ResultsTab(self, self.db)

        # Connect ManuBar actions
        self.controller.save_action.disconnect()
        self.controller.export_action.disconnect()
        self.controller.save_action.triggered.connect(
            self.results_tab.save_results)
        self.controller.export_action.triggered.connect(
            self.results_tab.export_results)

        self.initUI()

    def initUI(self) -> None:
        """
        UI Setup  
        """
        self.tabs.addTab(self.upload_tab, "Upload")
        self.tabs.addTab(self.res_tab, "Residential Properties")
        self.tabs.addTab(self.non_res_tab, "Non-Residential Properties")
        self.tabs.addTab(self.ascii_tab, "ASCII Grids")
        self.tabs.addTab(self.node_tab, "Nodes")
        self.tabs.addTab(self.results_tab, "Results")

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.tabs)
        self.setLayout(main_lyt)

    def return_home(self) -> None:
        """
        Leave detailed appraisal widget
        """
        # Ask for confirmation
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("All unsaved results will be lost")
        msgbox.setInformativeText("Do you want to proceed?")
        msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.Yes)
        retval = msgbox.exec_()

        if retval == QMessageBox.Yes:
            # Exit appraisal
            self.controller.select_page(0)

    def load_appraisal(self, fname: str) -> None:
        """
        Load database fields from arg fname 
        """
        if fname:
            # Only run if file is selected

            # Multithreading process
            # Instantiate thread and worker
            self.thread = QThread()
            self.worker = JSONLoadWorker(self, fname)
            self.worker.moveToThread(self.thread)

            # Connect signals
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.load_appraisal_error)

            # Start thread
            self.thread.start()

            # Enable and disable display during task
            self.tabs.setDisabled(True)
            self.thread.finished.connect(lambda: self.tabs.setEnabled(True))

            # Reload displays upon task finishing
            self.thread.finished.connect(self.res_tab.display_props)
            self.thread.finished.connect(self.non_res_tab.display_props)
            self.thread.finished.connect(self.ascii_tab.display_asciis)
            self.thread.finished.connect(self.node_tab.display_nodes)
            self.thread.finished.connect(self.upload_tab.update_upload_counts)
            self.thread.finished.connect(self.upload_tab.update_event_details)
            self.thread.finished.connect(self.results_tab.update_table)
            self.thread.finished.connect(self.results_tab.update_totals)
            self.thread.finished.connect(self.res_tab.display_checks)
            self.thread.finished.connect(self.non_res_tab.display_checks)
            self.thread.finished.connect(self.node_tab.display_checks)

    def load_appraisal_error(self, e: Exception) -> None:
        """
        Display traceback if errors occur during execution of appraisal loading
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("An error occured during while loading this appraisal")
        msgbox.setDetailedText(f"Traceback: {e}")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setEscapeButton(QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Ok)
        msgbox.exec_()


"""
####################
######## TABS ######
####################
"""


class UploadTab(QWidget):
    def __init__(self, parent: DetailedAppraisal, db: DetailedDataHandler) -> None:
        super().__init__()

        self.parent = parent
        self.db = db

        # Upload counts
        self.res_count_label = QLabel()
        self.non_res_count_label = QLabel()
        self.ascii_count_label = QLabel()
        self.node_count_label = QLabel()
        self.update_upload_counts()

        # Details labels
        self.event_type_label = QLabel()
        self.evac_cost_label = QLabel()
        self.location_label = QLabel()
        self.scheme_lifetime_label = QLabel()
        self.sop_label = QLabel()
        self.cellar_label = QLabel()
        self.damage_cap_label = QLabel()
        self.res_cap_label = QLabel()
        self.non_res_cap_label = QLabel()
        self.rp_label = QLabel()

        # Multithreading fields
        self.ascii_upload_btn = QPushButton("Upload Dataset")
        self.ascii_progress_label = QLabel()
        self.upload_prop_dataset_btn = QPushButton("Upload Dataset")
        self.prop_progress_label = QLabel()
        self.node_upload_btn = QPushButton("Upload Flood Event Shapefiles")
        self.node_progress_label = QLabel()

        # Update labels
        self.update_event_details()

        self.initUI()

    def initUI(self) -> None:
        """
        UI Setup  
        """
        # Property Upload Groupbox
        prop_upload_group = QGroupBox("Upload Properties")
        self.upload_prop_dataset_btn.clicked.connect(self.upload_prop_dataset)
        upload_prop_manual_btn = QPushButton("Upload Property Manually")
        upload_prop_manual_btn.clicked.connect(self.upload_prop_manual)
        self.res_count_label.setAlignment(Qt.AlignCenter)
        self.non_res_count_label.setAlignment(Qt.AlignCenter)
        self.prop_progress_label.setAlignment(Qt.AlignCenter)
        self.prop_progress_label.hide()
        prop_upload_lyt = QGridLayout()
        prop_upload_lyt.setColumnStretch(0, 1)
        prop_upload_lyt.setColumnStretch(3, 1)
        prop_upload_lyt.setRowStretch(0, 1)
        prop_upload_lyt.setRowStretch(4, 1)
        prop_upload_lyt.addWidget(self.res_count_label, 1, 1, 1, 2)
        prop_upload_lyt.addWidget(self.non_res_count_label, 2, 1, 1, 2)
        prop_upload_lyt.addWidget(self.upload_prop_dataset_btn, 3, 1, 1, 1)
        prop_upload_lyt.addWidget(upload_prop_manual_btn, 3, 2, 1, 1)
        prop_upload_lyt.addWidget(self.prop_progress_label, 4, 1, 1, 2)
        prop_upload_group.setLayout(prop_upload_lyt)

        # ASCII Grid Upload Groupbox
        ascii_upload_group = QGroupBox("Upload ASCII Grids")
        self.ascii_upload_btn.clicked.connect(self.upload_ascii)
        self.ascii_count_label.setAlignment(Qt.AlignCenter)
        self.ascii_progress_label.setAlignment(Qt.AlignCenter)
        self.ascii_progress_label.hide()
        ascii_upload_lyt = QVBoxLayout()
        ascii_upload_lyt.addStretch()
        ascii_upload_lyt.addWidget(self.ascii_count_label)
        ascii_upload_lyt.addLayout(utils.centered_hbox(self.ascii_upload_btn))
        ascii_upload_lyt.addWidget(self.ascii_progress_label)
        ascii_upload_lyt.addStretch()
        ascii_upload_group.setLayout(ascii_upload_lyt)

        # Flood shapefile Upload Groupbox
        node_upload_group = QGroupBox("Upload Flood Event Shapefiles")
        self.node_upload_btn.clicked.connect(self.upload_node_dataset)
        self.node_count_label.setAlignment(Qt.AlignCenter)
        self.node_progress_label.setAlignment(Qt.AlignCenter)
        self.node_progress_label.hide()
        node_upload_lyt = QVBoxLayout()
        node_upload_lyt.addStretch()
        node_upload_lyt.addWidget(self.node_count_label)
        node_upload_lyt.addLayout(utils.centered_hbox(self.node_upload_btn))
        node_upload_lyt.addWidget(self.node_progress_label)
        node_upload_group.setLayout(node_upload_lyt)
        node_upload_lyt.addStretch()

        details_group = QGroupBox("Flood Event Details")
        edit_details_btn = QPushButton("Edit Flood Event Details")
        edit_details_btn.clicked.connect(self.edit_event_details)
        self.event_type_label.setAlignment(Qt.AlignCenter)
        self.evac_cost_label.setAlignment(Qt.AlignCenter)
        self.location_label.setAlignment(Qt.AlignCenter)
        self.scheme_lifetime_label.setAlignment(Qt.AlignCenter)
        self.sop_label.setAlignment(Qt.AlignCenter)
        self.cellar_label.setAlignment(Qt.AlignCenter)
        self.damage_cap_label.setAlignment(Qt.AlignCenter)
        self.res_cap_label.setAlignment(Qt.AlignCenter)
        self.non_res_cap_label.setAlignment(Qt.AlignCenter)
        self.rp_label.setAlignment(Qt.AlignCenter)
        details_lyt = QGridLayout()
        details_lyt.setColumnStretch(0, 1)
        details_lyt.setColumnStretch(3, 1)
        details_lyt.setRowStretch(0, 1)
        details_lyt.setRowStretch(9, 1)
        details_lyt.addWidget(self.rp_label, 1, 1, 1, 2)
        details_lyt.addWidget(self.event_type_label, 2, 1, 1, 2)
        details_lyt.addWidget(self.scheme_lifetime_label, 3, 1, 1, 1)
        details_lyt.addWidget(self.sop_label, 3, 2, 1, 1)
        details_lyt.addWidget(self.evac_cost_label, 4, 1, 1, 1)
        details_lyt.addWidget(self.location_label, 4, 2, 1, 1)
        details_lyt.addWidget(self.cellar_label, 5, 1, 1, 1)
        details_lyt.addWidget(self.damage_cap_label, 5, 2, 1, 1)
        details_lyt.addWidget(self.res_cap_label, 6, 1, 1, 2)
        details_lyt.addWidget(self.non_res_cap_label, 7, 1, 1, 2)
        details_lyt.addLayout(utils.centered_hbox(
            edit_details_btn), 8, 1, 1, 2)
        details_group.setLayout(details_lyt)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QGridLayout()
        main_lyt.setSpacing(25)
        main_lyt.addWidget(prop_upload_group, 1, 1, 1, 1)
        main_lyt.addWidget(ascii_upload_group, 2, 1, 1, 1)
        main_lyt.addWidget(node_upload_group, 3, 1, 1, 1)
        main_lyt.addWidget(details_group, 1, 0, 3, 1)
        main_lyt.addLayout(utils.centered_hbox(home_btn), 5, 0, 1, 2)

        self.setLayout(main_lyt)

    def update_upload_counts(self) -> None:
        """
        Update labels displaying number of datapoints uploaded 
        """
        self.res_count_label.setText(
            f"Residential Properties Uploaded: {self.db.res_count}")
        self.non_res_count_label.setText(
            f"Non-Residential Properties Uploaded: {self.db.non_res_count}")
        self.ascii_count_label.setText(
            f"ASCII Grids Uploaded: {self.db.ascii_count}")
        self.node_count_label.setText(
            f"Flood Shapefile Datapoints Uploaded: {self.db.node_count}")

    def upload_prop_manual(self) -> None:
        """
        Get all prop info from user, add to db if save button pressed 
        """
        popup = PropManualUpload(self)

        # Update db if save is pressed
        if popup.exec_():
            mcm = popup.mcm_entry.currentText().split("-")[0]
            prop_details = [entry.text() for entry in popup.entries] + [mcm]

            # Add property details
            self.db.add_prop(prop_details)

        self.update_upload_counts()
        self.parent.res_tab.display_props()
        self.parent.non_res_tab.display_props()

    def get_prop_fname(self) -> Tuple[str, str]:
        """ Instanciate file dialog widget for user to select property/node dataset

        Returns:
            str: Selected filename and filetype, empty strings if dialog is closed before file is selected
        """
        file_types = "CSVs (*.csv);;DBFs (*.dbf)"
        return QFileDialog.getOpenFileName(self, "Select Dataset", "", file_types)

    def upload_prop_dataset(self) -> None:
        """
        Get filename from user and instantiate dialog
        """
        fname = self.get_prop_fname()

        # Only run if file is selected
        if fname[0]:
            popup = PropDatasetUpload(self, fname)

            # Run
            if popup.exec_():

                # Instantiate thread and worker
                self.thread = QThread()
                worker = PropUploadWorker(self, popup.columns, popup.table)
                worker.moveToThread(self.thread)

                # Connect signals
                self.thread.started.connect(worker.run)
                worker.finished.connect(self.thread.quit)
                worker.finished.connect(worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                worker.progress.connect(self.prop_progress_update)
                worker.error.connect(self.prop_upload_error)

                # Start thread
                self.thread.start()

                # Resets
                self.upload_prop_dataset_btn.setDisabled(True)
                self.prop_progress_label.show()
                self.thread.finished.connect(
                    lambda: self.upload_prop_dataset_btn.setEnabled(True))
                self.thread.finished.connect(self.prop_progress_label.hide)

                # Reload displays
                self.thread.finished.connect(self.update_upload_counts)
                self.thread.finished.connect(self.parent.res_tab.display_props)
                self.thread.finished.connect(
                    self.parent.non_res_tab.display_props)

    def prop_upload_error(self, e: Exception) -> None:
        """
        Display traceback if errors occur during execution of prop upload
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("An error occured while uploading the dataset")
        msgbox.setDetailedText(f"Traceback: {e}")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setEscapeButton(QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Ok)
        msgbox.exec_()

    def prop_progress_update(self, progess_pct: float) -> None:
        """
        Update users on progress of long-running prop-upload task
        """
        self.prop_progress_label.setText(
            f"Upload progress: {round(progess_pct*100)}%")

    def get_ascii_fnames(self) -> List[str]:
        """ Instanciate file dialog widget for user to select ascii grid(s)

        Returns:
            List[str]: Selected filenames
        """
        file_types = "ASCII Grids (*.asc)"

        # Discard file type
        return QFileDialog.getOpenFileNames(self, "Select ASCII Grids", "", file_types)[0]

    def upload_ascii(self) -> None:
        """
        Get ASCII filenames and upload to database
        """
        fnames = self.get_ascii_fnames()

        # Instantiate thread and worker
        self.thread = QThread()
        worker = AsciiWorker(self, fnames)
        worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(worker.run)
        worker.finished.connect(self.thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        worker.progress.connect(self.ascii_progress_update)
        worker.error.connect(self.ascii_upload_error)

        # Start self.thread
        self.thread.start()

        # Resets
        self.ascii_upload_btn.setDisabled(True)
        self.ascii_progress_label.show()
        self.thread.finished.connect(
            lambda: self.ascii_upload_btn.setEnabled(True))
        self.thread.finished.connect(self.ascii_progress_label.hide)

        # Reload displays
        self.thread.finished.connect(self.update_upload_counts)
        self.thread.finished.connect(self.parent.ascii_tab.display_asciis)

    def ascii_upload_error(self, e: Exception, fname: str) -> None:
        """
        Display traceback if errors occur during execution of ascii upload
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText(
            f"An error occured while uploading the following file: {fname}")
        msgbox.setDetailedText(f"Traceback: {e}")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setEscapeButton(QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Ok)
        msgbox.exec_()

    def ascii_progress_update(self, progress_pct: float) -> None:
        """
        Update users on progress of long-running ASCII upload task
        """
        self.ascii_progress_label.setText(
            f"Upload progress: {round(progress_pct*100)}%")

    def upload_node_dataset(self) -> None:
        """
        Get filename from user and instantiate dialog 
        """
        fname = self.get_prop_fname()

        # Only run if file is selected
        if fname[0]:
            popup = NodeDatasetUpload(self, fname, self.db)

            # Run
            if popup.exec_():

                # Instantiate thread and worker
                self.thread = QThread()
                worker = NodeUploadWorker(self, popup.columns, popup.table)
                worker.moveToThread(self.thread)

                # Connect signals
                self.thread.started.connect(worker.run)
                worker.finished.connect(self.thread.quit)
                worker.finished.connect(worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                worker.progress.connect(self.node_progress_update)
                worker.error.connect(self.node_upload_error)

                # Start thread
                self.thread.start()

                # Resets
                self.node_upload_btn.setDisabled(True)
                self.node_progress_label.show()
                self.thread.finished.connect(
                    lambda: self.node_upload_btn.setEnabled(True))
                self.thread.finished.connect(self.node_progress_label.hide)

                # Reload displays
                self.thread.finished.connect(self.update_upload_counts)
                self.thread.finished.connect(
                    self.parent.node_tab.display_nodes)

    def node_upload_error(self, e: Exception) -> None:
        """
        Display traceback if errors occur during execution of node upload
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("An error occured while uploading the dataset")
        msgbox.setDetailedText(f"Traceback: {e}")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setEscapeButton(QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Ok)
        msgbox.exec_()

    def node_progress_update(self, progress_pct: float) -> None:
        """
        Update users on progress of long-running node-upload task
        """
        self.node_progress_label.setText(
            f"Upload progress: {round(progress_pct*100)}%")

    def update_event_details(self) -> None:
        """
        Reload display of flood information labels
        """
        # Text updates
        self.event_type_label.setText(
            "Event Type: {}".format(self.db.event_type))
        self.evac_cost_label.setText(
            "Evacuation Cost Category: {}".format(self.db.evac_cost_category))
        self.location_label.setText(
            "Location Type: {}".format(self.db.location))
        self.scheme_lifetime_label.setText(
            "Scheme Lifetime: {} years".format(self.db.scheme_lifetime))
        self.sop_label.setText(
            "Standard of Protection: {} years".format(self.db.sop))
        self.cellar_label.setText(
            "Non-Residential Cellars: {}".format("Enabled" if self.db.cellar else "Disabled"))
        self.res_cap_label.setText(
            "Average Residential Property Value: £{}".format(self.db.res_cap))
        self.non_res_cap_label.setText(
            "Average Non-Residential Property Value: £{}".format(self.db.non_res_cap))
        self.damage_cap_label.setText("Damage Capping: {}".format(
            "Enabled" if self.db.caps_enabled else "Disabled"))
        self.rp_label.setText("Return Periods (years): {}".format(
            ",  ".join([str(rp) for rp in self.db.return_periods])))

        # Enable/Disable caps
        if self.db.caps_enabled:
            self.res_cap_label.setEnabled(True)
            self.non_res_cap_label.setEnabled(True)
        else:
            self.res_cap_label.setDisabled(True)
            self.non_res_cap_label.setDisabled(True)

    def edit_event_details(self) -> None:
        """
        Run the EditFloodDetails dialog
        """
        popup = EditFloodDetails(self, self.db)

        if popup.exec_():
            # Save general flood information
            self.db.event_type = popup.event_type_entry.currentText()
            self.db.location = popup.location_entry.currentText()
            self.db.scheme_lifetime = popup.scheme_lifetime_entry.value()
            self.db.sop = popup.sop_entry.value()
            self.db.evac_cost_category = popup.evac_cost_entry.currentText()
            self.db.cellar = popup.cellar_entry.isChecked()

            # Save damage capping
            self.db.res_cap = int(popup.res_cap_entry.text())
            self.db.non_res_cap = int(popup.non_res_cap_entry.text())
            self.db.caps_enabled = popup.cap_enabled_entry.isChecked()

            # Save return periods
            self.db.return_periods = sorted(
                [int(entry.text()) for entry in popup.entries])

            # Update display
            self.update_event_details()


class ResidentialTab(QWidget):
    def __init__(self, parent: DetailedAppraisal, db: DetailedDataHandler) -> None:
        super().__init__()

        self.parent = parent
        self.db = db

        # Display fields
        self.address_labels = []
        self.town_labels = []
        self.mcm_labels = []
        self.ground_level_labels = []
        self.easting_labels = []
        self.northing_labels = []
        self.edit_btns = []
        self.lyts = []
        self.groups = []

        self.elevations_btn = QPushButton("Generate Ground Levels")
        self.elevations_label = QLabel()
        self.btn_lyt_1 = QHBoxLayout()
        self.scroll_area = QVBoxLayout()

        self.initUI()
        self.display_props()

    def initUI(self) -> None:
        """
        UI Setup  
        """
        text = QLabel(
            "Here you can select which residential properties you want to be included in your appraisal")
        text.setAlignment(Qt.AlignCenter)

        # Scroll area setup
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.scroll_area)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        self.elevations_btn.clicked.connect(self.get_elevations)
        self.elevations_btn.hide()

        self.elevations_label.setAlignment(Qt.AlignCenter)
        self.elevations_label.hide()

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(15)
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(self.btn_lyt_1))
        main_lyt.addWidget(scroll)
        main_lyt.addLayout(utils.centered_hbox(self.elevations_btn))
        main_lyt.addWidget(self.elevations_label)
        main_lyt.addLayout(utils.centered_hbox(home_btn))
        self.setLayout(main_lyt)

    def display_prop(self, index: int) -> None:
        """
        Reload display of single property 
        """
        # Access property info from db
        easting = self.db.res_eastings[index]
        northing = self.db.res_northings[index]
        address = self.db.res_addresses[index]
        town = self.db.res_towns[index]
        postcode = self.db.res_postcodes[index]
        mcm = self.db.res_mcms[index]
        ground_level = self.db.res_ground_levels[index]

        # Update labels
        self.easting_labels[index].setText("Easting: {}".format(easting))
        self.northing_labels[index].setText("Northing: {}".format(northing))
        self.address_labels[index].setText("Address: {}".format(address))
        self.town_labels[index].setText("Town: {} - {}".format(town, postcode))
        self.mcm_labels[index].setText(
            "MCM Code: {} - {}".format(mcm, utils.get_res_mcm(mcm)))
        self.ground_level_labels[index].setText(
            "Ground Level: {}".format(ground_level))

    def display_props(self) -> None:
        """
        Reload display of all uploaded props in scroll area
        """
        # Remove all groupboxes currently in scroll area
        for i in reversed(range(self.scroll_area.count())):
            self.scroll_area.itemAt(i).widget().setParent(None)

        eastings = self.db.res_eastings
        northings = self.db.res_northings
        addresses = self.db.res_addresses
        towns = self.db.res_towns
        postcodes = self.db.res_postcodes
        mcms = self.db.res_mcms
        ground_levels = self.db.res_ground_levels
        prop_count = self.db.res_count

        # Build (de)select all buttons if properties have been uploaded
        self.build_btns(prop_count)

        # Build temp if no properties uploaded
        if prop_count == 0:
            self.build_temp()
            return

        # Write over old labels
        self.easting_labels = [QLabel("Easting: {}".format(i))
                               for i in eastings]
        self.northing_labels = [
            QLabel("Northing: {}".format(i)) for i in northings]
        self.address_labels = [QLabel("Address: {}".format(i))
                               for i in addresses]
        self.town_labels = [QLabel(
            "Town: {} - {}".format(towns[i], postcodes[i])) for i in range(prop_count)]
        self.mcm_labels = [
            QLabel("MCM Code: {} - {}".format(i, utils.get_res_mcm(i))) for i in mcms]
        self.ground_level_labels = [
            QLabel("Ground Level: {}".format(i)) for i in ground_levels]

        # Write over other widgets
        self.edit_btns = [QPushButton("Edit") for _ in range(prop_count)]
        self.lyts = [QGridLayout() for _ in range(prop_count)]
        self.groups = [QGroupBox("Residential Property {}".format(i+1))
                       for i in range(prop_count)]

        for i in range(prop_count):
            # Label formatting
            self.easting_labels[i].setFixedWidth(175)
            self.easting_labels[i].setWordWrap(True)
            self.northing_labels[i].setFixedWidth(175)
            self.northing_labels[i].setWordWrap(True)
            self.address_labels[i].setFixedWidth(350)
            self.address_labels[i].setWordWrap(True)
            self.town_labels[i].setFixedWidth(350)
            self.town_labels[i].setWordWrap(True)
            self.mcm_labels[i].setFixedWidth(175)
            self.mcm_labels[i].setWordWrap(True)
            self.ground_level_labels[i].setFixedWidth(175)
            self.ground_level_labels[i].setWordWrap(True)

            # Button connections
            self.edit_btns[i].clicked.connect(partial(self.edit_prop, i))

            # Layout setup
            self.lyts[i].setColumnStretch(0, 1)
            self.lyts[i].setColumnStretch(5, 1)
            self.lyts[i].addWidget(self.address_labels[i], 0, 1, 1, 1)
            self.lyts[i].addWidget(self.town_labels[i], 1, 1, 1, 1)
            self.lyts[i].addWidget(self.mcm_labels[i], 0, 2, 1, 1)
            self.lyts[i].addWidget(self.ground_level_labels[i], 1, 2, 1, 1)
            self.lyts[i].addWidget(self.easting_labels[i], 0, 3, 1, 1)
            self.lyts[i].addWidget(self.northing_labels[i], 1, 3, 1, 1)
            self.lyts[i].addWidget(self.edit_btns[i], 0, 4, 2, 1)

            # Groupbox setup
            self.groups[i].setCheckable(True)
            self.groups[i].setLayout(self.lyts[i])
            self.scroll_area.addWidget(self.groups[i])

    def display_elevations(self) -> None:
        """
        Reload display of elevation labels, used after automatic elevation generation 
        """
        for i in range(self.db.res_count):
            self.ground_level_labels[i].setText(
                "Ground Level: {}".format(self.db.res_ground_levels[i]))

    def build_temp(self) -> None:
        """
        Add label if no properties are uploaded 
        """
        text = QLabel(
            "You haven't uploaded any residential properties yet\n\nAdd some from the Upload Tab to begin")
        text.setAlignment(Qt.AlignCenter)
        self.scroll_area.addWidget(text)

    def build_btns(self, prop_count: int) -> None:
        """
        Build and connect (de)select buttons if properties have been uploaded 
        """
        # Remove all widgets currently in layouts
        for i in reversed(range(self.btn_lyt_1.count())):
            self.btn_lyt_1.itemAt(i).widget().setParent(None)

        if prop_count != 0:
            # Only create buttons if properties have been uploaded
            select_btn = QPushButton("Select All")
            select_btn.clicked.connect(lambda: self.select_groups(True))
            deselect_btn = QPushButton("Deselect All")
            deselect_btn.clicked.connect(lambda: self.select_groups(False))

            # Add to layouts
            self.btn_lyt_1.addWidget(select_btn)
            self.btn_lyt_1.addWidget(deselect_btn)

            # Make btn visisble
            self.elevations_btn.show()

    def select_groups(self, state: bool) -> None:
        """
        Set all groups to the arg checked state
        """
        for group in self.groups:
            group.setChecked(state)

    def edit_prop(self, index: int) -> None:
        """
        Edit details of property   
        """
        popup = EditResPropDetails(self, self.db, index)

        if popup.exec_():
            mcm = popup.mcm_entry.currentText().split("-")[0]
            prop_details = [entry.text()
                            for entry in popup.entries[:-1:]] + [mcm]
            gl = popup.entries[-1].text()

            # Update database
            self.db.edit_res(prop_details, gl, index)

            # Update display
            self.display_prop(index)

        self.parent.upload_tab.update_upload_counts()

    def get_elevations(self) -> None:
        """
        Get prop elevations from ASCII grids 
        """
        # Ask for confirmation
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setText(
            "This will automatically calculate Ground Levels of residential properties based on the uploaded ASCII grids")
        msgbox.setInformativeText("Do you want to proceed?")
        msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.Yes)
        retval = msgbox.exec_()

        if retval == QMessageBox.Yes:
            # Generate elevations
            self.db.get_res_elevations()

            # Display warning of properties not covered by ASCIIs
            none_count = sum([x is None for x in self.db.res_ground_levels])
            if none_count != 0:
                msgbox_2 = QMessageBox(self)
                msgbox_2.setWindowModality(Qt.WindowModal)
                msgbox_2.setIcon(QMessageBox.Warning)
                msgbox_2.setText("Ground Levels could not be calculated for {} residential {}".format(
                    none_count, "property" if none_count == 1 else "properties"))
                msgbox_2.setInformativeText(
                    "Try uploading more ASCII grids or setting Ground Levels manually")
                msgbox_2.setStandardButtons(QMessageBox.Ok)
                msgbox_2.exec_()

                self.elevations_label.setText("Ground levels could not be found for: {} residential {}".format(
                    none_count, "property" if none_count == 1 else "properties"))
                self.elevations_label.show()

            # No warnings needed
            if none_count == 0:
                self.elevations_label.hide()

            # Reload display
            self.display_elevations()

    def get_checks(self) -> None:
        """
        Find checked properties with valid ground level entries
        """
        checked_props = [group.isChecked() for group in self.groups]
        valid_gls = [gl is not None for gl in self.db.res_ground_levels]

        self.db.res_checks = [checked_props[i] and valid_gls[i]
                              for i in range(len(checked_props))]
        self.db.clean_res_count = len([x for x in self.db.res_checks if x])

    def display_checks(self) -> None:
        """
        Enable/Disable self.groups based on checks 
        Used for reloading display after appraisal loads
        """
        for i in range(self.db.res_count):
            self.groups[i].setChecked(self.db.res_checks[i])


class NonResidentialTab(QWidget):
    def __init__(self, parent: DetailedAppraisal, db: DetailedDataHandler) -> None:
        super().__init__()

        self.parent = parent
        self.db = db

        # Display fields
        self.easting_labels = []
        self.northing_labels = []
        self.address_labels = []
        self.town_labels = []
        self.mcm_labels = []
        self.floor_area_labels = []
        self.ground_level_labels = []
        self.edit_btns = []
        self.lyts = []
        self.groups = []

        self.elevations_btn = QPushButton("Generate Ground Levels")
        self.elevations_label = QLabel()
        self.btn_lyt_1 = QHBoxLayout()
        self.scroll_area = QVBoxLayout()

        self.initUI()
        self.display_props()

    def initUI(self) -> None:
        """
        UI Setup  
        """
        text = QLabel(
            "Here you can select which non-residential properties you want to be included in your appraisal")
        text.setAlignment(Qt.AlignCenter)

        # Scroll area setup
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.scroll_area)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        self.elevations_btn.clicked.connect(self.get_elevations)
        self.elevations_btn.hide()

        self.elevations_label.setAlignment(Qt.AlignCenter)
        self.elevations_label.hide()

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(15)
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(self.btn_lyt_1))
        main_lyt.addWidget(scroll)
        main_lyt.addLayout(utils.centered_hbox(self.elevations_btn))
        main_lyt.addWidget(self.elevations_label)
        main_lyt.addLayout(utils.centered_hbox(home_btn))
        self.setLayout(main_lyt)

    def display_prop(self, index: int) -> None:
        """
        Update display of single property 
        """
        # Access property info from db
        easting = self.db.non_res_eastings[index]
        northing = self.db.non_res_northings[index]
        address = self.db.non_res_addresses[index]
        town = self.db.non_res_towns[index]
        postcode = self.db.non_res_postcodes[index]
        mcm = self.db.non_res_mcms[index]
        floor_area = self.db.non_res_floor_areas[index]
        ground_level = self.db.non_res_ground_levels[index]

        # Update labels
        self.easting_labels[index].setText("Easting: {}".format(easting))
        self.northing_labels[index].setText("Northing: {}".format(northing))
        self.address_labels[index].setText("Address: {}".format(address))
        self.town_labels[index].setText("Town: {} - {}".format(town, postcode))
        self.mcm_labels[index].setText(
            "MCM Code: {} - {}".format(mcm, utils.get_non_res_mcm(mcm)))
        self.floor_area_labels[index].setText(
            "Floor Area: {}".format(floor_area))
        self.ground_level_labels[index].setText(
            "Ground Level: {}".format(ground_level))

    def display_props(self) -> None:
        """
        Display all uploaded props in scroll area 
        """
        # Remove all groupboxes currently in scroll area
        for i in reversed(range(self.scroll_area.count())):
            self.scroll_area.itemAt(i).widget().setParent(None)

        eastings = self.db.non_res_eastings
        northings = self.db.non_res_northings
        addresses = self.db.non_res_addresses
        towns = self.db.non_res_towns
        postcodes = self.db.non_res_postcodes
        mcms = self.db.non_res_mcms
        floor_areas = self.db.non_res_floor_areas
        ground_levels = self.db.non_res_ground_levels
        prop_count = self.db.non_res_count

        # Build (de)select all buttons if properties have been uploaded
        self.build_btns(prop_count)

        # Build temp if no properties are uploaded
        if prop_count == 0:
            self.build_temp()
            return

        # Write over old labels
        self.easting_labels = [QLabel("Easting: {}".format(i))
                               for i in eastings]
        self.northing_labels = [
            QLabel("Northing: {}".format(i)) for i in northings]
        self.address_labels = [QLabel("Address: {}".format(i))
                               for i in addresses]
        self.town_labels = [QLabel(
            "Town: {} - {}".format(towns[i], postcodes[i])) for i in range(prop_count)]
        self.mcm_labels = [
            QLabel("MCM Code: {} - {}".format(i, utils.get_non_res_mcm(i))) for i in mcms]
        self.floor_area_labels = [
            QLabel("Floor Area: {}".format(i)) for i in floor_areas]
        self.ground_level_labels = [
            QLabel("Ground Level: {}".format(i)) for i in ground_levels]

        # Write over other widgets
        self.edit_btns = [QPushButton("Edit") for _ in range(prop_count)]
        self.lyts = [QGridLayout() for _ in range(prop_count)]
        self.groups = [QGroupBox(
            "Non-Residential Property {}".format(i+1)) for i in range(prop_count)]

        for i in range(prop_count):
            # Label formatting
            self.easting_labels[i].setFixedWidth(175)
            self.easting_labels[i].setWordWrap(True)
            self.northing_labels[i].setFixedWidth(175)
            self.northing_labels[i].setWordWrap(True)
            self.address_labels[i].setFixedWidth(350)
            self.address_labels[i].setWordWrap(True)
            self.town_labels[i].setFixedWidth(350)
            self.town_labels[i].setWordWrap(True)
            self.mcm_labels[i].setFixedWidth(175)
            self.mcm_labels[i].setWordWrap(True)
            self.floor_area_labels[i].setFixedWidth(175)
            self.floor_area_labels[i].setWordWrap(True)
            self.ground_level_labels[i].setFixedWidth(175)
            self.ground_level_labels[i].setWordWrap(True)

            # Button connections
            self.edit_btns[i].clicked.connect(partial(self.edit_prop, i))

            # Layout setup
            self.lyts[i].setColumnStretch(0, 1)
            self.lyts[i].setColumnStretch(6, 1)
            self.lyts[i].addWidget(self.address_labels[i], 0, 1, 1, 1)
            self.lyts[i].addWidget(self.town_labels[i], 1, 1, 1, 1)
            self.lyts[i].addWidget(self.mcm_labels[i], 0, 2, 1, 1)
            self.lyts[i].addWidget(self.ground_level_labels[i], 1, 2, 1, 1)
            self.lyts[i].addWidget(self.easting_labels[i], 0, 3, 1, 1)
            self.lyts[i].addWidget(self.northing_labels[i], 1, 3, 1, 1)
            self.lyts[i].addWidget(self.floor_area_labels[i], 0, 4, 2, 1)
            self.lyts[i].addWidget(self.edit_btns[i], 0, 5, 2, 1)

            # Groupbox setup
            self.groups[i].setCheckable(True)
            self.groups[i].setLayout(self.lyts[i])
            self.scroll_area.addWidget(self.groups[i])

    def display_elevations(self) -> None:
        """
        Reload display of elevation labels, used after automatic elevation generation
        """
        for i in range(self.db.non_res_count):
            self.ground_level_labels[i].setText(
                "Ground Level: {}".format(self.db.non_res_ground_levels[i]))

    def build_temp(self) -> None:
        """
        Add label if no properties are uploaded
        """
        text = QLabel(
            """You haven't uploaded any non-residential properties yet\n\nAdd some from the Upload Tab to begin""")
        text.setAlignment(Qt.AlignCenter)
        self.scroll_area.addWidget(text)

    def build_btns(self, prop_count: int) -> None:
        """
        Build and connect (de)select buttons if properties have been uploaded 
        """
        # Remove all widgets currently in property
        for i in reversed(range(self.btn_lyt_1.count())):
            self.btn_lyt_1.itemAt(i).widget().setParent(None)

        if prop_count != 0:
            # Only create buttons if properties have been uploaded
            select_btn = QPushButton("Select All")
            select_btn.clicked.connect(lambda: self.select_groups(True))
            deselect_btn = QPushButton("Deselect All")
            deselect_btn.clicked.connect(lambda: self.select_groups(False))

            # Add to layouts
            self.btn_lyt_1.addWidget(select_btn)
            self.btn_lyt_1.addWidget(deselect_btn)

            # Make btn visible
            self.elevations_btn.show()

    def select_groups(self, state: bool) -> None:
        """
        Set all groups to the arg checked state 
        """
        for group in self.groups:
            group.setChecked(state)

    def edit_prop(self, index: int) -> None:
        """
        Edit details of property
        """
        popup = EditNonResPropDetails(self, self.db, index)

        if popup.exec_():
            mcm = popup.mcm_entry.currentText().split("-")[0]
            prop_details = [entry.text()
                            for entry in popup.entries[:-1:]] + [mcm]
            gl = popup.entries[-1].text()

            # Update database
            self.db.edit_non_res(prop_details, gl, index)

            # Update displat
            self.display_prop(index)

        self.parent.upload_tab.update_upload_counts()

    def get_elevations(self) -> None:
        """
        Get prop elevations from ASCII grids
        """
        # Ask for confirmation
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setText(
            "This will automatically calculate Ground Levels of non-residential properties based on the uploaded ASCII grids")
        msgbox.setInformativeText("D you want to proceed?")
        msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.Yes)
        retval = msgbox.exec_()

        if retval == QMessageBox.Yes:
            # Generate elevations
            self.db.get_non_res_elevations()

            # DIsplay warning of properties not covered by ASCIIs
            none_count = sum(
                [x is None for x in self.db.non_res_ground_levels])
            if none_count != 0:
                msgbox_2 = QMessageBox(self)
                msgbox_2.setWindowModality(Qt.WindowModal)
                msgbox_2.setIcon(QMessageBox.Warning)
                msgbox_2.setText("Ground Levels could not be calculated for {} non-residential {}".format(
                    none_count, "property" if none_count == 1 else "properties"))
                msgbox_2.setInformativeText(
                    "Try uploading more ASCII grids or setting Ground Levels manually")
                msgbox_2.setStandardButtons(QMessageBox.Ok)
                msgbox_2.setEscapeButton(QMessageBox.Ok)
                msgbox_2.setDefaultButton(QMessageBox.No)
                msgbox_2.exec_()

                self.elevations_label.setText("Ground Levels could not be found for: {} non-residential {}".format(
                    none_count, "property" if none_count == 1 else "properties"))
                self.elevations_label.show()

            # No warnings needed
            if none_count == 0:
                self.elevations_label.hide()

            # Reload display
            self.display_elevations()

    def get_checks(self) -> None:
        """
        Find checked properties with valid ground level entries
        """
        checked_props = [group.isChecked() for group in self.groups]
        valid_gls = [gl is not None for gl in self.db.non_res_ground_levels]

        self.db.non_res_checks = [checked_props[i] and valid_gls[i]
                                  for i in range(len(checked_props))]
        self.db.clean_non_res_count = len(
            [x for x in self.db.non_res_checks if x])

    def display_checks(self) -> None:
        """
        Enable/Disable self.groups based on checks
        Used for reloading display after appraisal loads
        """
        for i in range(self.db.non_res_count):
            self.groups[i].setChecked(self.db.non_res_checks[i])


class AsciiTab(QWidget):
    def __init__(self, parent: DetailedAppraisal, db: DetailedDataHandler) -> None:
        super().__init__()

        self.parent = parent
        self.db = db

        # Display fields
        self.fname_labels = []
        self.corner_labels = []
        self.n_col_labels = []
        self.n_row_labels = []
        self.cellsize_labels = []
        self.nodata_labels = []
        self.edit_btns = []
        self.lyts = []
        self.groups = []

        self.scroll_area = QVBoxLayout()

        self.initUI()
        self.display_asciis()

    def initUI(self) -> None:
        """ 
        UI Setup
        """
        text = QLabel("Here you can view your uploaded ASCII Grids")
        text.setAlignment(Qt.AlignCenter)

        # Scroll area setup
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.scroll_area)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(15)
        main_lyt.addWidget(text)
        main_lyt.addWidget(scroll)
        main_lyt.addLayout(utils.centered_hbox(home_btn))
        self.setLayout(main_lyt)

    def display_ascii(self, index: int) -> None:
        """
        Update display of single property
        """
        # Access ASCII info from db
        fname = self.db.ascii_fnames[index]
        x_corner = self.db.x_corners[index]
        y_corner = self.db.y_corners[index]
        n_col = self.db.n_cols[index]
        n_row = self.db.n_rows[index]
        cellsize = self.db.cellsizes[index]
        nodata_value = self.db.nodata_values[index]

        # Update labels
        self.fname_labels[index].setText("Filename: {}".format(fname))
        self.corner_labels[index].setText(
            "Corner: ({},  {})".format(x_corner, y_corner))
        self.n_col_labels[index].setText("Number of columns: {}".format(n_col))
        self.n_row_labels[index].setText("Number of rows: {}".format(n_row))
        self.cellsize_labels[index].setText("Cellsize: {}".format(cellsize))
        self.nodata_labels[index].setText(
            "Nodata value: {}".format(nodata_value))

    def display_asciis(self) -> None:
        """
        Display all uploaded asciis in scroll area 
        """
        # Remove all groupboxes currently in scroll area
        for i in reversed(range(self.scroll_area.count())):
            self.scroll_area.itemAt(i).widget().setParent(None)

        fnames = self.db.ascii_fnames
        x_corners = self.db.x_corners
        y_corners = self.db.y_corners
        n_cols = self.db.n_cols
        n_rows = self.db.n_rows
        cellsizes = self.db.cellsizes
        nodata_values = self.db.nodata_values
        ascii_count = self.db.ascii_count

        if ascii_count == 0:
            self.build_temp()
            return

        # Write over old labels
        self.fname_labels = [QLabel("Filename: {}".format(i)) for i in fnames]
        self.corner_labels = [QLabel("Corner: ({},  {})".format(
            x_corners[i], y_corners[i])) for i in range(ascii_count)]
        self.n_col_labels = [
            QLabel("Number of columns: {}".format(i)) for i in n_cols]
        self.n_row_labels = [
            QLabel("Number of rows: {}".format(i)) for i in n_rows]
        self.cellsize_labels = [
            QLabel("Cellsize: {}".format(i)) for i in cellsizes]
        self.nodata_labels = [QLabel("Nodata value: {}".format(i))
                              for i in nodata_values]

        # Write over other widgets
        self.edit_btns = [QPushButton("Edit") for _ in range(ascii_count)]
        self.lyts = [QGridLayout() for _ in range(ascii_count)]
        self.groups = [QGroupBox("ASCII Grid {}".format(i+1))
                       for i in range(ascii_count)]

        for i in range(ascii_count):
            # Label formatting
            self.fname_labels[i].setFixedWidth(350)
            self.fname_labels[i].setWordWrap(True)
            self.corner_labels[i].setFixedWidth(350)
            self.corner_labels[i].setWordWrap(True)
            self.n_col_labels[i].setFixedWidth(175)
            self.n_col_labels[i].setWordWrap(True)
            self.n_row_labels[i].setFixedWidth(175)
            self.n_row_labels[i].setWordWrap(True)
            self.cellsize_labels[i].setFixedWidth(175)
            self.cellsize_labels[i].setWordWrap(True)
            self.nodata_labels[i].setFixedWidth(175)
            self.nodata_labels[i].setWordWrap(True)

            # Button connections
            self.edit_btns[i].clicked.connect(partial(self.edit_ascii, i))

            # Layout setup
            self.lyts[i].setColumnStretch(0, 1)
            self.lyts[i].setColumnStretch(5, 1)
            self.lyts[i].addWidget(self.fname_labels[i], 0, 1, 1, 1)
            self.lyts[i].addWidget(self.corner_labels[i], 1, 1, 1, 1)
            self.lyts[i].addWidget(self.n_col_labels[i], 0, 2, 1, 1)
            self.lyts[i].addWidget(self.n_row_labels[i], 1, 2, 1, 1)
            self.lyts[i].addWidget(self.cellsize_labels[i], 0, 3, 1, 1)
            self.lyts[i].addWidget(self.nodata_labels[i], 1, 3, 1, 1)
            self.lyts[i].addWidget(self.edit_btns[i], 0, 4, 2, 1)

            # Groupbox setup
            self.groups[i].setLayout(self.lyts[i])
            self.scroll_area.addWidget(self.groups[i])

    def build_temp(self) -> None:
        """
        Add label if no grids are uploaded 
        """
        text = QLabel(
            """You haven't uploaded any ASCII grids yet\n\nAdd some from the Upload Tab to begin""")
        text.setAlignment(Qt.AlignCenter)
        self.scroll_area.addWidget(text)

    def edit_ascii(self, index: int) -> None:
        """ 
        Edit details of ASCII grid
        """
        popup = EditAsciiDetails(self, self.db, index)

        if popup.exec_():
            ascii_details = [entry.text() for entry in popup.entries]

            # Update database
            self.db.edit_ascii(ascii_details, index)

            # Update display
            self.display_ascii(index)

        self.parent.upload_tab.update_upload_counts()


class NodeTab(QWidget):
    def __init__(self, parent: DetailedAppraisal, db: DetailedDataHandler) -> None:
        super().__init__()
        self.parent = parent
        self.db = db

        # Dispaly fields
        self.eastings_labels = []
        self.northing_labels = []
        self.rp_labels = []
        self.depth_labels = []
        self.edit_btns = []
        self.lyts = []
        self.groups = []

        self.btn_lyt = QHBoxLayout()
        self.scroll_area = QVBoxLayout()

        self.initUI()
        self.display_nodes()

    def initUI(self) -> None:
        """
        UI Setup  
        """
        text = QLabel(
            "Here you can select which nodes you want to be included in your appraisal")
        text.setAlignment(Qt.AlignCenter)

        # Scroll area setup
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.scroll_area)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(15)
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(self.btn_lyt))
        main_lyt.addWidget(scroll)
        main_lyt.addLayout(utils.centered_hbox(home_btn))
        self.setLayout(main_lyt)

    def display_node(self, index: int) -> None:
        """
        Update display of sisngle node
        """
        # Access node info from db
        easting = self.db.node_eastings[index]
        northing = self.db.node_northings[index]
        rps = self.db.return_periods
        depths = self.db.node_depths[index]

        # Update labels
        self.eastings_labels[index].setText("Easting: {}".format(easting))
        self.northing_labels[index].setText("Northing: {}".format(northing))
        for i in range(len(rps)):
            self.depth_labels[index][i].setText(str(depths[i]))

    def display_nodes(self) -> None:
        """
        Display all uploaded nodes in scroll area 
        """
        # Remove all groupboxes currently in scroll area
        for i in reversed(range(self.scroll_area.count())):
            self.scroll_area.itemAt(i).widget().setParent(None)

        eastings = self.db.node_eastings
        northings = self.db.node_northings
        rps = self.db.return_periods
        depths = self.db.node_depths
        node_count = self.db.node_count
        rp_count = len(self.db.return_periods)

        # Build de(select) all buttons if properties have been uploaded
        self.build_btns(node_count)

        # Build temp if no nodes uploaded
        if node_count == 0:
            self.build_temp()
            return

        # Write over old labels
        self.eastings_labels = [
            QLabel("Easting: {}".format(i)) for i in eastings]
        self.northing_labels = [
            QLabel("Norting: {}".format(i)) for i in northings]
        self.rp_labels = [[QLabel("{} year FE depth:".format(rp))
                           for rp in rps] for _ in range(node_count)]
        self.depth_labels = [
            [QLabel(str(depth)) for depth in sub_depth] for sub_depth in depths]

        # Write over other widgets
        self.edit_btns = [QPushButton("Edit") for _ in range(node_count)]
        self.lyts = [QGridLayout() for _ in range(node_count)]
        self.groups = [QGroupBox("Node {}".format(i+1))
                       for i in range(node_count)]

        for i in range(node_count):
            # Label formatting
            self.eastings_labels[i].setFixedWidth(200)
            self.eastings_labels[i].setWordWrap(True)
            self.northing_labels[i].setFixedWidth(200)
            self.northing_labels[i].setWordWrap(True)

            for j in range(rp_count):
                self.rp_labels[i][j].setFixedWidth(125)
                self.rp_labels[i][j].setWordWrap(True)
                self.depth_labels[i][j].setFixedWidth(125)
                self.depth_labels[i][j].setWordWrap(True)

            # Button connections
            self.edit_btns[i].clicked.connect(partial(self.edit_node, i))

            # Layout setup
            self.lyts[i].setColumnStretch(0, 1)
            self.lyts[i].setColumnStretch(rp_count+3, 1)
            self.lyts[i].addWidget(self.eastings_labels[i], 0, 1, 1, 1)
            self.lyts[i].addWidget(self.northing_labels[i], 1, 1, 1, 1)

            for j in range(rp_count):
                self.lyts[i].addWidget(self.rp_labels[i][j], 0, j+2, 1, 1)
                self.lyts[i].addWidget(self.depth_labels[i][j], 1, j+2, 1, 1)

            self.lyts[i].addWidget(self.edit_btns[i], 0, rp_count+2, 2, 1)

            # Groupbox setup
            self.groups[i].setCheckable(True)
            self.groups[i].setLayout(self.lyts[i])
            self.scroll_area.addWidget(self.groups[i])

    def build_temp(self) -> None:
        """
        Add label if no nodes are uploaded 
        """
        text = QLabel(
            "You haven't uploaded any nodes yet\n\nAdd some from the Upload Tab to begin")
        text.setAlignment(Qt.AlignCenter)
        self.scroll_area.addWidget(text)

    def build_btns(self, node_count: int) -> None:
        """
        Build and connect (de)select buttons if properties have been uploaded 
        """
        # FEmove all widgets currently added
        for i in reversed(range(self.btn_lyt.count())):
            self.btn_lyt.itemAt(i).widget().setParent(None)

        if node_count != 0:
            # Create and connecr btns
            select_btn = QPushButton("Select all")
            select_btn.clicked.connect(lambda: self.select_groups(True))
            deselect_btn = QPushButton("Deselect All")
            deselect_btn.clicked.connect(lambda: self.select_groups(False))

            # Add to layouts
            self.btn_lyt.addWidget(select_btn)
            self.btn_lyt.addWidget(deselect_btn)

    def select_groups(self, state: bool) -> None:
        """
        Set all groups to the arg checked state
        """
        for group in self.groups:
            group.setChecked(state)

    def edit_node(self, index: int) -> None:
        """
        Edit details of node
        """
        popup = EditNodeDetails(self, self.db, index)

        if popup.exec_():
            node_details = [entry.text() for entry in popup.entries]

            # Update database
            self.db.edit_node(node_details, index)

            # Update display
            self.display_node(index)

        self.parent.upload_tab.update_upload_counts()

    def get_checks(self) -> None:
        """
        Get checked state of each flood shapefile node
        """
        self.db.node_checks = [group.isChecked() for group in self.groups]
        self.db.clean_node_count = len([x for x in self.db.node_checks if x])

    def display_checks(self) -> None:
        """
        Enable/Disable self.groups based on checks 
        Used for reloading display after appraisal loads
        """
        for i in range(self.db.node_count):
            self.groups[i].setChecked(self.db.node_checks[i])


class ResultsTab(QWidget):
    def __init__(self, parent: DetailedAppraisal, db: DetailedDataHandler) -> None:
        super().__init__()
        self.parent = parent
        self.db = db

        # Display fields
        self.table = QTableWidget()
        self.average_annual_label = QLabel()
        self.lifetime_label = QLabel()

        self.save_results_btn = QPushButton("Save Appraisal")

        self.initUI()

        self.update_table()
        self.update_totals()

    def initUI(self) -> None:
        """
        UI Setup  
        """
        # Generate table headings and set size
        col_headings = [
            "Existing\nAnnual Damage (£)",
            "Existing\nLifetime Damage (£)",
            "Post Intervention\nAnnual Damage (£)",
            "Post Intervention\nLifetime Damage (£)",
            "Benefits\nAnnual (£)",
            "Benefits\nLifetime (£)"]
        row_headings = [
            "Residential",
            "Intangible",
            "Mental Health",
            "Vehicular",
            "Evacuation",
            "Non-Residential",
            "Business Disruption",
            "Infrastructure",
            "Emergency Services & Recovery",
            "Total"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumWidth(875)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        text = QLabel("From here you can generate,  view,  and export results")
        text.setAlignment(Qt.AlignCenter)

        # Results Groupbox
        results_group = QGroupBox("Results")
        get_results_btn = QPushButton("Generate Results")
        get_results_btn.clicked.connect(self.get_results)
        self.average_annual_label.setAlignment(Qt.AlignCenter)
        self.lifetime_label.setAlignment(Qt.AlignCenter)
        results_lyt = QVBoxLayout()
        results_lyt.addLayout(utils.centered_hbox(get_results_btn))
        results_lyt.addWidget(self.table)
        label_lyt = QHBoxLayout()
        label_lyt.addStretch()
        label_lyt.addWidget(self.average_annual_label)
        label_lyt.addStretch()
        label_lyt.addWidget(self.lifetime_label)
        label_lyt.addStretch()
        results_lyt.addLayout(label_lyt)
        results_group.setLayout(results_lyt)

        # Advanced Groupbox
        advanced_group = QGroupBox("Advanced")
        view_damages_btn = QPushButton("View Damages Breakdown")
        view_damages_btn.clicked.connect(self.get_damages_breakdown)
        view_benefits_btn = QPushButton("View Benefits Breakdown")
        view_benefits_btn.clicked.connect(self.get_benefits_breakdown)
        export_results_btn = QPushButton("Export Results")
        export_results_btn.clicked.connect(self.export_results)
        self.save_results_btn.clicked.connect(self.save_results)
        advanced_lyt = QGridLayout()
        advanced_lyt.addLayout(utils.centered_hbox(
            view_damages_btn), 0, 0, 1, 1)
        advanced_lyt.addLayout(utils.centered_hbox(
            view_benefits_btn), 1, 0, 1, 1)
        advanced_lyt.addLayout(utils.centered_hbox(
            export_results_btn), 0, 1, 1, 1)
        advanced_lyt.addLayout(utils.centered_hbox(
            self.save_results_btn), 1, 1, 1, 1)
        advanced_group.setLayout(advanced_lyt)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(25)
        main_lyt.addWidget(text)
        main_lyt.addWidget(results_group)
        main_lyt.addWidget(advanced_group)
        main_lyt.addLayout(utils.centered_hbox(home_btn))
        self.setLayout(main_lyt)

    def update_table(self) -> None:
        """
        Update display of self.table
        """
        datapoints = self.db.get_major_datapoints()
        for row in range(len(datapoints)):
            for col in range(len(datapoints[0])):
                item = QTableWidgetItem("{:,.2f}".format(datapoints[row][col]))
                self.table.setItem(row, col, item)

    def update_totals(self) -> None:
        """
        Update labels displaying flood damage totals
        """
        self.average_annual_label.setText(
            "Average Annual Benefit:  £{:,.2f}".format(self.db.total_current_annual_benefit))
        self.lifetime_label.setText(
            "Lifetime Benefit:  £{:,.2f}".format(self.db.total_current_lifetime_benefit))

    def get_results(self) -> None:
        """
        Generate results for currently selected properties, nodes, and flood-event details
        """
        # Update checks
        self.parent.res_tab.get_checks()
        self.parent.non_res_tab.get_checks()
        self.parent.node_tab.get_checks()

        invalid_count = self.db.res_count + self.db.non_res_count - \
            self.db.clean_res_count - self.db.clean_non_res_count

        if invalid_count != 0:
            # Invalid properites exist, confirmation needed
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Question)
            msgbox.setText(
                f"{invalid_count} properties are deselected or do not have valid ground level entries. These will not be included in results calculations")
            msgbox.setInformativeText("Do you want to proceed?")
            msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msgbox.setDefaultButton(QMessageBox.Yes)
            msgbox.setEscapeButton(QMessageBox.No)

            # Ask for confirmation
            retval = msgbox.exec_()
            if retval == QMessageBox.No:
                return

        if self.db.node_count == 0:
            # No nodes uploaded
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("Results could not be calculated")
            msgbox.setInformativeText("No flood nodes have been uploaded")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.exec_()
            return

        # Update results fields
        self.db.get_damages()
        self.db.get_benefits()

        # Update displays
        self.update_table()
        self.update_totals()

    def get_damages_breakdown(self) -> None:
        """
        Run the DamagesBreakdown dialog
        """
        popup = DamagesBreakdown(self, self.db)
        popup.exec_()

    def get_benefits_breakdown(self) -> None:
        """
        Run the BenefitsBreakdown dialog
        """
        popup = BenefitsBreakdown(self, self.db)
        popup.exec_()

    def export_results(self) -> None:
        """
        Run the ExportResults dialog
        """
        popup = ExportResults(self)

        if popup.exec_():
            # Save button pressed
            fname = popup.path
            damage_options = [btn.isChecked() for btn in popup.damage_btns]
            benefit_options = [btn.isChecked() for btn in popup.benefit_btns]
            file_formats = [btn.isChecked() for btn in popup.file_btns]

            # Write files
            self.db.export_results(fname, damage_options,
                                   benefit_options, file_formats)
            utils.write_method_caveats(
                "detailed", os.path.join(fname, "Notes"))

    def save_results(self) -> None:
        """
        Save appraisal to .trit file
        """
        fname = utils.get_save_fname(self)

        if fname:
            # Only run if file is selected

            # Instaniate thread and worker
            self.thread = QThread()
            self.worker = JSONWriteWorker(self, fname)
            self.worker.moveToThread(self.thread)

            # Connect signals
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.save_error)

            # Start thread
            self.thread.start()

            # Reset displays
            self.save_results_btn.setDisabled(True)
            self.thread.finished.connect(
                lambda: self.save_results_btn.setEnabled(True))

    def save_error(self, e: Exception) -> None:
        """
        Display traceback if errors occur during execution of JSON writing
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("An error occured while saving the results")
        msgbox.setDetailedText(f"Traceback: {e}")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setEscapeButton(QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Ok)
        msgbox.exec_()


"""
####################
###### DIALOGS #####
####################
"""


class PropDatasetUpload(QDialog):
    def __init__(self, parent: UploadTab, fname: List[str]) -> None:
        super().__init__(parent)

        self.parent = parent
        self.fname = fname

        self.columns = [1] * 8
        self.table = QTableWidget()

        self.build_table()
        self.initUI()
        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.parent.frameGeometry().size())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel(
            "Here you can view and manually edit your uploaded dataset")
        text.setAlignment(Qt.AlignCenter)

        preview_btn = QPushButton("Preview Properties Found")
        preview_btn.clicked.connect(self.preview_props)
        select_btn = QPushButton("Select Columns")
        select_btn.clicked.connect(self.select_columns)
        btn_lyt_1 = QHBoxLayout()
        btn_lyt_1.addWidget(preview_btn)
        btn_lyt_1.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        btn_lyt_2 = QHBoxLayout()
        btn_lyt_2.addWidget(cancel_btn)
        btn_lyt_2.addWidget(save_btn)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(15)
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_1))
        main_lyt.addWidget(self.table)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_2))
        self.setLayout(main_lyt)

    def build_table(self) -> None:
        """  
        Build QTableWidget() and insert into UI
        """
        if self.fname[1] == "CSVs (*.csv)":
            self.table = utils.table_from_csv(self.fname)
        else:
            self.table = utils.table_from_dbf(self.fname)

    def select_columns(self) -> None:
        """
        Run the SelectPropColumns dialog 
        """
        popup = SelectPropColumns(self)

        # Read entries if dialog is saved
        if popup.exec_():
            self.columns = [int(entry.text()) for entry in popup.entries]

    def preview_props(self) -> None:
        """
        Run the PreviewPropDataset dialog 
        """
        popup = PreviewPropDataset(self)
        popup.exec_()


class NodeDatasetUpload(QDialog):
    def __init__(self, parent: UploadTab, fname: List[str], db: DetailedDataHandler) -> None:
        super().__init__(parent)

        self.parent = parent
        self.fname = fname
        self.db = db

        # +2 added for easting and northing entries
        self.columns = [1] * (len(self.db.return_periods) + 2)
        self.table = QTableWidget()

        self.build_table()
        self.initUI()
        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.parent.frameGeometry().size())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel(
            "Here you can view and manually edit your uploaded dataset")
        text.setAlignment(Qt.AlignCenter)

        preview_btn = QPushButton("Preview Nodes Found")
        preview_btn.clicked.connect(self.preview_nodes)
        select_btn = QPushButton("Select Columns")
        select_btn.clicked.connect(self.select_columns)
        btn_lyt_1 = QHBoxLayout()
        btn_lyt_1.addWidget(preview_btn)
        btn_lyt_1.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        btn_lyt_2 = QHBoxLayout()
        btn_lyt_2.addWidget(cancel_btn)
        btn_lyt_2.addWidget(save_btn)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(15)
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_1))
        main_lyt.addWidget(self.table)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_2))
        self.setLayout(main_lyt)

    def build_table(self) -> None:
        """
        Build QTableWidget() and insert into UI 
        """
        if self.fname[1] == "CSVs (*.csv)":
            self.table = utils.table_from_csv(self.fname)
        else:
            self.table = utils.table_from_dbf(self.fname)

    def select_columns(self) -> None:
        """ 
        Run the SelectNodeColumns dialog
        """
        popup = SelectNodeColumns(self)

        # Read entries if dialog is saved
        if popup.exec_():
            self.columns = [int(entry.text()) for entry in popup.entries]

    def preview_nodes(self) -> None:
        """
        Run the PreviewNodeDataset dialog
        """
        popup = PreviewNodeDataset(self)
        popup.exec_()


class SelectPropColumns(QDialog):
    def __init__(self, parent: PropDatasetUpload) -> None:
        super().__init__(parent)

        self.parent = parent

        self.setWindowModality(Qt.WindowModal)

        self.texts = [
            "EASTINGS data - Column",
            "NORTHINGS data - Column",
            "PRIMARY ADDRESS data - Column",
            "SECONDARY ADDRESS data - Column",
            "TOWN data - Column",
            "POSTCODE data - Column",
            "FLOOR AREA data - Column",
            "MCM data - Column"
        ]
        self.entries = [QSpinBox() for _ in range(len(self.texts))]

        self.initUI()

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel(
            "Select the columns from your dataset that contain important information")
        text.setAlignment(Qt.AlignCenter)

        labels = [QLabel(text) for text in self.texts]
        column_count = self.parent.table.columnCount()
        for i in range(len(self.entries)):
            self.entries[i].setMinimum(1)
            self.entries[i].setMaximum(column_count)
            self.entries[i].setMinimumWidth(30)

            # Set entries to previously entered column values
            self.entries[i].setValue(int(self.parent.columns[i]))

        form_lyt = QFormLayout()
        for i in range(len(self.texts)):
            form_lyt.addRow(labels[i], self.entries[i])

        btns = QDialogButtonBox()
        btns.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(form_lyt)
        main_lyt.addLayout(utils.centered_hbox(btns))
        self.setLayout(main_lyt)


class SelectNodeColumns(QDialog):
    def __init__(self, parent: NodeDatasetUpload) -> None:
        super().__init__(parent)

        self.parent = parent

        self.setWindowModality(Qt.WindowModal)

        general_texts = [
            "EASTING data - Column",
            "NORTHING data - Column"]
        variable_texts = [
            "{} YEAR FE DEPTH data - Column".format(rp) for rp in self.parent.db.return_periods]
        self.texts = general_texts + variable_texts
        self.entries = [QSpinBox() for _ in range(len(self.texts))]

        self.initUI()

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """ 
        UI Setup
        """
        text = QLabel(
            "Select the columns from your dataset that contain important information")
        text.setAlignment(Qt.AlignCenter)

        labels = [QLabel(text) for text in self.texts]
        column_count = self.parent.table.columnCount()
        for i in range(len(self.entries)):
            self.entries[i].setMinimum(1)
            self.entries[i].setMaximum(column_count)
            self.entries[i].setMinimumWidth(30)

            # Set entries to previously entered column values
            self.entries[i].setValue(int(self.parent.columns[i]))

        form_lyt = QFormLayout()
        for i in range(len(self.texts)):
            form_lyt.addRow(labels[i], self.entries[i])

        btns = QDialogButtonBox()
        btns.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(form_lyt)
        main_lyt.addLayout(utils.centered_hbox(btns))
        self.setLayout(main_lyt)


class PreviewPropDataset(QDialog):
    def __init__(self, parent: PropDatasetUpload) -> None:
        super().__init__(parent)

        self.parent = parent

        self.res_count_label = QLabel()
        self.non_res_count_label = QLabel()
        self.table = QTableWidget()

        self.build_table()
        self.update_prop_count()
        self.initUI()
        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.frameGeometry().size())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel("The following properties were found in your dataset")
        text.setAlignment(Qt.AlignCenter)
        self.res_count_label.setAlignment(Qt.AlignCenter)
        self.non_res_count_label.setAlignment(Qt.AlignCenter)

        btn = QPushButton("Exit")
        btn.clicked.connect(self.reject)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addWidget(self.res_count_label)
        main_lyt.addWidget(self.non_res_count_label)
        main_lyt.addWidget(self.table)
        main_lyt.addLayout(utils.centered_hbox(btn))
        self.setLayout(main_lyt)

    def build_table(self) -> None:
        """
        Build table of clean properties found in parent 
        """
        headings = const.table_headings

        # Read and clean table
        all_rows = utils.read_table_with_columns(
            self.parent.columns,
            self.parent.table)
        valid_rows = [row for row in all_rows if utils.is_valid_res(
            row) or utils.is_valid_non_res(row)]

        self.table = utils.table_from_list(headings, valid_rows)

    def update_prop_count(self) -> None:
        """
        Update res and non-res property count labels 
        """
        mcms = []
        for row in range(self.table.rowCount()):
            cell = self.table.item(row, 7)
            mcms.append(int(cell.text()))

        self.res_count_label.setText(
            f"Residential Properties Found: {utils.res_count(mcms)}"
        )
        self.non_res_count_label.setText(
            f"Non-Residential Properties Found: {utils.non_res_count(mcms)}"
        )


class PreviewNodeDataset(QDialog):
    def __init__(self, parent: NodeDatasetUpload) -> None:
        super().__init__(parent)

        self.parent = parent

        self.node_count_label = QLabel()
        self.table = QTableWidget()

        self.build_table()
        self.update_node_count()
        self.initUI()
        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.frameGeometry().size())

    def initUI(self) -> None:
        """ 
        UI Setup
        """
        text = QLabel("The following nodes were found in your dataset")
        text.setAlignment(Qt.AlignCenter)
        self.node_count_label.setAlignment(Qt.AlignCenter)

        btn = QPushButton("Exit")
        btn.clicked.connect(self.reject)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addWidget(self.node_count_label)
        main_lyt.addWidget(self.table)
        main_lyt.addLayout(utils.centered_hbox(btn))
        self.setLayout(main_lyt)

    def build_table(self) -> None:
        """
        Build table of clean nodes found in parent 
        """
        headings = ["Easting", "Northing"]
        for rp in self.parent.db.return_periods:
            headings += [f"{rp} year FE depth"]
        all_rows = utils.read_table_with_columns(
            self.parent.columns,
            self.parent.table)
        valid_rows = [row for row in all_rows if utils.is_valid_node(row)]

        self.table = utils.table_from_list(headings, valid_rows)

    def update_node_count(self) -> None:
        """
        Update node count labels 
        """
        self.node_count_label.setText(f"Nodes Found: {self.table.rowCount()}")


class PropManualUpload(QDialog):
    def __init__(self, parent: UploadTab) -> None:
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.prop_is_res = True
        self.texts = [
            "Easting",
            "Northing",
            "Primary Address",
            "Secondary Address",
            "Town",
            "Postcode",
            "Floor Area",
            "MCM Code"]
        self.labels = [QLabel(text) for text in self.texts]
        self.entries = [QLineEdit() for _ in range(len(self.texts)-1)]
        self.mcm_entry = QComboBox()

        self.res_mcm_options = [
            "{} - {}".format(key, const.res_mcm[key]) for key in const.res_mcm]
        self.non_res_mcm_options = [
            "{} - {}".format(key, const.non_res_mcm[key]) for key in const.non_res_mcm]

        self.initUI()

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel("Enter the details of the property to be uploaded below")
        text.setAlignment(Qt.AlignCenter)
        res_btn = QRadioButton("Residential Property")
        res_btn.setChecked(True)
        res_btn.clicked.connect(self.switch_prop_type)
        non_res_btn = QRadioButton("Non-Residential Property")
        non_res_btn.clicked.connect(self.switch_prop_type)

        # Spinbox setup
        self.mcm_entry.addItems(self.res_mcm_options)

        form_lyt = QFormLayout()
        # Add all lineedit entries
        for i in range(len(self.entries)):
            form_lyt.addRow(self.labels[i], self.entries[i])

        # Add spinbox entry
        form_lyt.addRow(self.labels[-1], self.mcm_entry)

        # Set floor area widgets to disabled initially
        self.labels[-2].setDisabled(True)
        self.entries[-1].setDisabled(True)

        # Easting, Northing, GL, and FA validators
        float_validator = QDoubleValidator(-10000000.0, 10000000.0, 5)
        self.entries[0].setValidator(float_validator)
        self.entries[1].setValidator(float_validator)
        self.entries[6].setValidator(float_validator)

        btn_lyt = QDialogButtonBox()
        btn_lyt.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btn_lyt.accepted.connect(self.check_entries)
        btn_lyt.rejected.connect(self.reject)

        main_lyt = QGridLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text, 0, 0, 1, 2)
        main_lyt.addLayout(utils.centered_hbox(res_btn), 1, 0, 1, 2)
        main_lyt.addLayout(utils.centered_hbox(non_res_btn), 2, 0, 1, 2)

        for i in range(len(self.entries)):
            # Add line edit entries
            self.labels[i].setAlignment(Qt.AlignRight)
            main_lyt.addWidget(self.labels[i], 3+i, 0)
            main_lyt.addWidget(self.entries[i], 3+i, 1)

        # Add combobox entry
        self.labels[-1].setAlignment(Qt.AlignRight)
        main_lyt.addWidget(self.labels[-1], 10, 0)
        main_lyt.addWidget(self.mcm_entry, 10, 1)

        # Add Cancel and Save buttons
        main_lyt.addLayout(utils.centered_hbox(btn_lyt), 11, 0, 1, 2)
        self.setLayout(main_lyt)

    def switch_prop_type(self) -> None:
        """
        Switch between res/non-res property types
        """
        # Enable/Disable floor area entries
        if self.prop_is_res:
            self.labels[-2].setEnabled(True)
            self.entries[-1].setEnabled(True)

            # Update MCM options
            for i in reversed(range(len(self.res_mcm_options))):
                self.mcm_entry.removeItem(i)

            self.mcm_entry.addItems(self.non_res_mcm_options)

        else:
            self.labels[-2].setDisabled(True)
            self.entries[-1].setDisabled(True)

            # Update MCM options
            for i in reversed(range(len(self.non_res_mcm_options))):
                self.mcm_entry.removeItem(i)

            self.mcm_entry.addItems(self.res_mcm_options)

        self.prop_is_res = not self.prop_is_res

    def check_entries(self) -> None:
        """ 
        Check required entries are valid
        """
        # Get entered details
        mcm = self.mcm_entry.currentText().split("-")[0]
        prop_details = [entry.text() for entry in self.entries] + [mcm]

        # Valid residential property
        if self.prop_is_res and utils.is_valid_res(prop_details):
            self.accept()

        # Valid non-residential property
        elif not self.prop_is_res and utils.is_valid_non_res(prop_details):
            self.accept()

        else:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            if self.prop_is_res:
                msgbox.setText(
                    "Easting and Northing entries must be valid numbers.")
            else:
                msgbox.setText(
                    "Easting,  Northing,  and Floor Area entries must be valid numbers.")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.exec_()


class EditResPropDetails(QDialog):
    def __init__(self, parent: ResidentialTab, db: DetailedDataHandler, index: int) -> None:
        super().__init__(parent)

        self.parent = parent
        self.db = db
        self.index = index

        self.datapoints = [
            "Easting",
            "Northing",
            "Address",
            "Town",
            "Postcode",
            "Ground Level",
            "MCM Code"
        ]
        self.entries = [QLineEdit() for _ in range(len(self.datapoints)-1)]
        self.mcm_entry = QComboBox()

        self.initUI()
        self.setWindowModality(Qt.WindowModal)

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup  
        """
        text = QLabel(
            "Edit the property information for Residential Property {}".format(self.index+1))
        text.setAlignment(Qt.AlignCenter)

        labels = [QLabel(datapoint) for datapoint in self.datapoints]

        res_mcm_options = [
            "{} - {}".format(key, const.res_mcm[key]) for key in const.res_mcm]
        self.mcm_entry.addItems(res_mcm_options)

        # Set entries to current data values
        self.entries[0].setText(str(self.db.res_eastings[self.index]))
        self.entries[1].setText(str(self.db.res_northings[self.index]))
        self.entries[2].setText(self.db.res_addresses[self.index])
        self.entries[3].setText(self.db.res_towns[self.index])
        self.entries[4].setText(self.db.res_postcodes[self.index])
        self.entries[5].setText(str(self.db.res_ground_levels[self.index])
                                if self.db.res_ground_levels[self.index] else None)
        self.mcm_entry.setCurrentIndex(
            list(const.res_mcm.keys()).index(self.db.res_mcms[self.index]))

        # Validator
        float_validator = QDoubleValidator(-10000000.0, 10000000.0, 5)
        self.entries[0].setValidator(float_validator)
        self.entries[1].setValidator(float_validator)
        self.entries[5].setValidator(float_validator)

        entry_lyt = QGridLayout()
        for i in range(len(self.entries)):
            # Add line edit entries
            labels[i].setAlignment(Qt.AlignRight)
            entry_lyt.addWidget(labels[i], i, 0)
            entry_lyt.addWidget(self.entries[i], i, 1)

        # Add combobox entry
        labels[-1].setAlignment(Qt.AlignRight)
        entry_lyt.addWidget(labels[-1], 6, 0)
        entry_lyt.addWidget(self.mcm_entry, 6, 1)

        btn_lyt = QDialogButtonBox()
        btn_lyt.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btn_lyt.accepted.connect(self.check_entries)
        btn_lyt.rejected.connect(self.reject)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_property)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(entry_lyt)
        main_lyt.addLayout(utils.centered_hbox(delete_btn))
        main_lyt.addLayout(utils.centered_hbox(btn_lyt))
        self.setLayout(main_lyt)

    def check_entries(self) -> None:
        """
        Check entries are valid before updating prop information 
        """
        mcm = self.mcm_entry.currentText().split("-")[0]
        # Discard ground level entry from testing
        entries = [entry.text() for entry in self.entries[:-1:]] + [mcm]
        # Insert temporary secondary address item
        entries.insert(3, "temp")
        # Insert temporary floor area item
        entries.insert(6, "temp")

        if utils.is_valid_res(entries):
            self.accept()
        else:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText(
                "Easting and Northing entries must be valid numbers.")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.exec_()

    def delete_property(self) -> None:
        """
        Confirmation and deletion of property 
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("Are you sure you want to delete this property?")
        msgbox.setInformativeText("This cannot be undone")
        msgbox.setStandardButtons(
            QMessageBox.No |
            QMessageBox.Yes)
        msgbox.setDefaultButton(QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)

        returnval = msgbox.exec_()
        if returnval == QMessageBox.Yes:
            # Delete record from database
            self.db.delete_res(self.index)

            # Reload display
            self.parent.display_props()

            # Reject so db isn't updated from entries
            self.reject()


class EditNonResPropDetails(QDialog):
    def __init__(self, parent: NonResidentialTab, db: DetailedDataHandler, index: int) -> None:
        super().__init__(parent)

        self.parent = parent
        self.db = db
        self.index = index

        self.datapoints = [
            "Easting",
            "Northing",
            "Address",
            "Town",
            "Postcode",
            "Floor Area",
            "Ground Level",
            "MCM Code"
        ]
        self.entries = [QLineEdit() for _ in range(len(self.datapoints)-1)]
        self.mcm_entry = QComboBox()

        self.initUI()
        self.setWindowModality(Qt.WindowModal)

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel(
            "Edit the property information for Non-Residential Property {}".format(self.index+1))
        text.setAlignment(Qt.AlignCenter)

        labels = [QLabel(datapoint) for datapoint in self.datapoints]

        non_res_mcm_options = [
            "{} - {}".format(key, const.non_res_mcm[key]) for key in const.non_res_mcm]
        self.mcm_entry.addItems(non_res_mcm_options)

        # Set entries to current data values
        self.entries[0].setText(str(self.db.non_res_eastings[self.index]))
        self.entries[1].setText(str(self.db.non_res_northings[self.index]))
        self.entries[2].setText(self.db.non_res_addresses[self.index])
        self.entries[3].setText(self.db.non_res_towns[self.index])
        self.entries[4].setText(self.db.non_res_postcodes[self.index])
        self.entries[5].setText(str(self.db.non_res_floor_areas[self.index]))
        self.entries[6].setText(str(self.db.non_res_ground_levels[self.index])
                                if self.db.non_res_ground_levels[self.index] else None)
        self.mcm_entry.setCurrentIndex(
            list(const.non_res_mcm.keys()).index(self.db.non_res_mcms[self.index]))

        # Validator
        float_validator = QDoubleValidator(-10000000.0, 10000000.0, 5)
        self.entries[0].setValidator(float_validator)
        self.entries[1].setValidator(float_validator)
        self.entries[5].setValidator(float_validator)
        self.entries[6].setValidator(float_validator)

        entry_lyt = QGridLayout()
        for i in range(len(self.entries)):
            # Add line edit entries
            labels[i].setAlignment(Qt.AlignRight)
            entry_lyt.addWidget(labels[i], i, 0)
            entry_lyt.addWidget(self.entries[i], i, 1)

        # Add combobox entry
        labels[-1].setAlignment(Qt.AlignRight)
        entry_lyt.addWidget(labels[-1], 7, 0)
        entry_lyt.addWidget(self.mcm_entry, 7, 1)

        btn_lyt = QDialogButtonBox()
        btn_lyt.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btn_lyt.accepted.connect(self.check_entries)
        btn_lyt.rejected.connect(self.reject)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_property)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(entry_lyt)
        main_lyt.addLayout(utils.centered_hbox(delete_btn))
        main_lyt.addLayout(utils.centered_hbox(btn_lyt))
        self.setLayout(main_lyt)

    def check_entries(self) -> None:
        """
        Check entries are valid before updating prop information 
        """
        mcm = self.mcm_entry.currentText().split("-")[0]
        # Discard ground level entry from testing
        entries = [entry.text() for entry in self.entries[:-1:]] + [mcm]
        # Insert temporary secondary address item
        entries.insert(3, "temp")

        if utils.is_valid_non_res(entries):
            self.accept()
        else:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText(
                "Easting,  Northing,  and Floor Area entries must be valid numbers.")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.exec_()

    def delete_property(self) -> None:
        """
        Confirmation and deletion of property 
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("Are you sure you want to delete this property?")
        msgbox.setInformativeText("This cannot be undone")
        msgbox.setStandardButtons(
            QMessageBox.No |
            QMessageBox.Yes)
        msgbox.setDefaultButton(QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)

        returnval = msgbox.exec_()
        if returnval == QMessageBox.Yes:
            # Delete record from database
            self.db.delete_non_res(self.index)

            # Reload display
            self.parent.display_props()

            # Reject so db is not updated from entries
            self.reject()


class EditAsciiDetails(QDialog):
    def __init__(self, parent: AsciiTab, db: DetailedDataHandler, index: int) -> None:
        super().__init__(parent)

        self.parent = parent
        self.db = db
        self.index = index

        self.datapoints = [
            "Name",
            "X Corner",
            "Y Corner",
            "Cellsize",
        ]
        self.entries = [QLineEdit() for _ in range(len(self.datapoints))]

        self.initUI()
        self.setWindowModality(Qt.WindowModal)

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel(
            "Edit information for ASCII grid {}".format(self.index+1))
        text.setAlignment(Qt.AlignCenter)

        labels = [QLabel(datapoint) for datapoint in self.datapoints]

        # Set entries to current data values
        # All entries except fname cast to str for testing as bool(0) == False
        # bool('0') == True however
        self.entries[0].setText(self.db.ascii_fnames[self.index])
        self.entries[1].setText(str(self.db.x_corners[self.index]) if str(
            self.db.x_corners[self.index]) else None)
        self.entries[2].setText(str(self.db.y_corners[self.index]) if str(
            self.db.y_corners[self.index]) else None)
        self.entries[3].setText(str(self.db.cellsizes[self.index]) if str(
            self.db.cellsizes[self.index]) else None)

        # Validators
        int_validator = QIntValidator(-10000000, 10000000)
        # X and Y corners, number of rows and cols, cellsize, and NODATA value validation
        for i in range(1, 4):
            self.entries[i].setValidator(int_validator)

        entry_lyt = QGridLayout()
        for i in range(len(self.entries)):
            labels[i].setAlignment(Qt.AlignRight)
            entry_lyt.addWidget(labels[i], i, 0)
            entry_lyt.addWidget(self.entries[i], i, 1)

        btn_lyt = QDialogButtonBox()
        btn_lyt.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btn_lyt.accepted.connect(self.accept)
        btn_lyt.rejected.connect(self.reject)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_ascii)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(entry_lyt)
        main_lyt.addLayout(utils.centered_hbox(delete_btn))
        main_lyt.addLayout(utils.centered_hbox(btn_lyt))
        self.setLayout(main_lyt)

    def check_entries(self) -> None:
        """
        Check entries are valid before updating ASCII information
        """
        if utils.is_valid_ascii([entry.text() for entry in self.entries]):
            self.accept()
        else:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("All entries must be valid numbers.")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.exec_()

    def delete_ascii(self) -> None:
        """ 
        Confirmation and deletion of ASCII grid
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("Are you sure you want to delete this ASCII grid?")
        msgbox.setInformativeText("This cannot be undone")
        msgbox.setStandardButtons(
            QMessageBox.No |
            QMessageBox.Yes)
        msgbox.setDefaultButton(QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)

        returnval = msgbox.exec_()
        if returnval == QMessageBox.Yes:
            # Delete record from database
            self.db.delete_ascii(self.index)

            # Relaod display
            self.parent.display_asciis()

            # Reject so db isn't updated from entries
            self.reject()


class EditNodeDetails(QDialog):
    def __init__(self, parent: NodeTab, db: DetailedDataHandler, index: int) -> None:
        super().__init__(parent)

        self.parent = parent
        self.db = db
        self.index = index

        self.datapoints = [
            "Easting",
            "Northing"] + [f"{rp} year depth" for rp in self.db.return_periods]
        self.entries = [QLineEdit() for _ in range(len(self.datapoints))]

        self.initUI()
        self.setWindowModality(Qt.WindowModal)

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel("Edit the details of Node {}".format(self.index+1))
        text.setAlignment(Qt.AlignCenter)

        labels = [QLabel(datapoint) for datapoint in self.datapoints]

        # Set entries to current data values
        # All datapoints cast to str for testing as bool(0) == False
        # bool('0') == True however
        self.entries[0].setText(str(self.db.node_eastings[self.index]) if str(
            self.db.node_eastings[self.index]) else None)
        self.entries[1].setText(str(self.db.node_northings[self.index]) if str(
            self.db.node_northings[self.index]) else None)
        for i in range(len(self.db.return_periods)):
            self.entries[i+2].setText(str(self.db.node_depths[self.index][i])
                                      if str(self.db.node_depths[self.index][i]) else None)

        # Validators
        float_validator = QDoubleValidator(-10000000.0, 10000000.0, 5)

        entry_lyt = QGridLayout()
        for i in range(len(self.entries)):
            labels[i].setAlignment(Qt.AlignRight)
            self.entries[i].setValidator(float_validator)

            # Add line edit entries
            entry_lyt.addWidget(labels[i], i, 0)
            entry_lyt.addWidget(self.entries[i], i, 1)

        btn_lyt = QDialogButtonBox()
        btn_lyt.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Save)
        btn_lyt.accepted.connect(self.check_entries)
        btn_lyt.rejected.connect(self.reject)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_node)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(entry_lyt)
        main_lyt.addLayout(utils.centered_hbox(delete_btn))
        main_lyt.addLayout(utils.centered_hbox(btn_lyt))
        self.setLayout(main_lyt)

    def check_entries(self) -> None:
        """
        Check entries are valid before updating node information
        """
        if utils.is_valid_node([entry.text() for entry in self.entries]):
            self.accept()
        else:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("All entries must be valid numbers.")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.exec_()

    def delete_node(self) -> None:
        """
        Confirmation and deletion of node 
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("Are you sure want to delete this node?")
        msgbox.setInformativeText("This cannot be undone")
        msgbox.setStandardButtons(
            QMessageBox.No |
            QMessageBox.Yes)
        msgbox.setDefaultButton(QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)

        returnval = msgbox.exec_()
        if returnval == QMessageBox.Yes:
            # Delete record from database
            self.db.delete_node(self.index)

            # Reload display
            self.parent.display_nodes()

            # Reject so db isn't updated from entries
            self.reject()


class EditFloodDetails(QDialog):
    def __init__(self, parent: UploadTab, db: DetailedDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Entry fields
        self.event_type_entry = QComboBox()
        self.location_entry = QComboBox()
        self.scheme_lifetime_entry = QSpinBox()
        self.sop_entry = QSpinBox()
        self.evac_cost_entry = QComboBox()
        self.cellar_entry = QCheckBox()
        self.res_cap_entry = QLineEdit()
        self.non_res_cap_entry = QLineEdit()
        self.cap_enabled_entry = QCheckBox()

        self.entries = []
        self.entry_lyt = QVBoxLayout()

        # Disabling/Enabling caps fields
        self.res_cap_label = QLabel("Average Residential Property Value")
        self.non_res_cap_label = QLabel(
            "Average Non-Residential Property Value")

        # Disabling/Enabling fe entry
        self.fe_group = QGroupBox("Flood Events")
        self.main_lyt = QGridLayout()

        self.setWindowModality(Qt.WindowModal)
        self.initUI()
        self.build_lyt()
        self.update_fields()
        self.update_fe()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel("Edit General Flood Information and Flood Events below")
        text.setAlignment(Qt.AlignCenter)

        # General information groupbox
        event_type_label = QLabel("Flood Event Type")
        location_label = QLabel("Location Type")
        scheme_lifetime_label = QLabel("Scheme Lifetime")
        sop_label = QLabel("Standard of Protection")
        evac_cost_label = QLabel("Evacuation Cost Category")
        cellar_label = QLabel("Non-Residential Property Cellars")

        event_types = [
            "Short Duration Major Flood Storm No Warning",
            "Short Duration Major Flood Storm <8hr Warning",
            "Short Duration Major Flood Storm >8hr Warning",
            "Long Duration Major Flood Storm No Warning",
            "Long Duration Major Flood Storm <8hr Warning",
            "Long Duration Major Flood Storm >8hr Warning",
            "Extra-Long Duration Major Flood Storm No Warning",
            "Extra-Long Duration Major Flood Storm <8hr Warning",
            "Extra-Long Duration Major Flood Storm >8hr Warning"
        ]
        self.event_type_entry.addItems(event_types)
        location_types = [
            "Rural",
            "Urban"
        ]
        self.location_entry.addItems(location_types)
        self.scheme_lifetime_entry.setMinimum(1)
        self.scheme_lifetime_entry.setMaximum(100)
        self.sop_entry.setMinimum(1)
        self.sop_entry.setMaximum(1000)
        evac_costs = [
            "Low",
            "Mid",
            "High"
        ]
        self.evac_cost_entry.addItems(evac_costs)

        general_lyt = QFormLayout()
        general_lyt.addRow(event_type_label, self.event_type_entry)
        general_lyt.addRow(scheme_lifetime_label, self.scheme_lifetime_entry)
        general_lyt.addRow(sop_label, self.sop_entry)
        general_lyt.addRow(location_label, self.location_entry)
        general_lyt.addRow(evac_cost_label, self.evac_cost_entry)
        general_lyt.addRow(cellar_label, self.cellar_entry)
        general_group = QGroupBox("General Flood Information")
        general_group.setLayout(general_lyt)

        # Damage capping groupbox
        cap_enabled_label = QLabel("Damage Cap Enabled")
        cap_enabled_label.setAlignment(Qt.AlignRight)

        self.cap_enabled_entry.clicked.connect(self.enable_cap)
        cap_validator = QIntValidator(0, 10000000)
        self.res_cap_label.setAlignment(Qt.AlignRight)
        self.res_cap_entry.setValidator(cap_validator)
        self.non_res_cap_label.setAlignment(Qt.AlignRight)
        self.non_res_cap_entry.setValidator(cap_validator)

        # Enable/Disable cap entries
        if not self.db.caps_enabled:
            self.res_cap_label.setDisabled(True)
            self.res_cap_entry.setDisabled(True)
            self.non_res_cap_label.setDisabled(True)
            self.non_res_cap_entry.setDisabled(True)

        damage_lyt = QFormLayout()
        damage_lyt.addRow(cap_enabled_label, self.cap_enabled_entry)
        damage_lyt.addRow(self.res_cap_label, self.res_cap_entry)
        damage_lyt.addRow(self.non_res_cap_label, self.non_res_cap_entry)
        damage_group = QGroupBox("Damage Capping")
        damage_group.setLayout(damage_lyt)

        # Flood Events groupbox
        remove_btn = QPushButton("Remove Flood Event")
        remove_btn.clicked.connect(self.remove_fe)
        add_btn = QPushButton("Add Flood Event")
        add_btn.clicked.connect(self.add_fe)
        btn_lyt_1 = QHBoxLayout()
        btn_lyt_1.addWidget(remove_btn)
        btn_lyt_1.addWidget(add_btn)

        fe_lyt = QVBoxLayout()
        fe_lyt.addLayout(self.entry_lyt)
        fe_lyt.addStretch()
        fe_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_1))
        self.fe_group.setLayout(fe_lyt)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        btn_lyt_2 = QHBoxLayout()
        btn_lyt_2.addWidget(cancel_btn)
        btn_lyt_2.addWidget(save_btn)

        self.main_lyt.addWidget(text, 0, 0, 1, 2)
        self.main_lyt.addWidget(general_group, 1, 0, 1, 1)
        self.main_lyt.addWidget(damage_group, 2, 0, 1, 1)
        self.main_lyt.addWidget(self.fe_group, 1, 1, 2, 1)
        self.main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_2), 4, 0, 1, 2)

        self.setLayout(self.main_lyt)

    def build_lyt(self) -> None:
        """
        Build flood events into self.entry_lyt
        """
        # Remove all widgets currently in lyt
        for i in reversed(range(self.entry_lyt.count())):
            self.entry_lyt.itemAt(i).widget().setParent(None)

        # Rebuild entries
        entry_count = len(self.db.return_periods)
        self.entries = [QSpinBox() for _ in range(entry_count)]
        for i in range(entry_count):
            self.entries[i].setMinimum(1)
            self.entries[i].setMaximum(1000)
            self.entries[i].setValue(self.db.return_periods[i])
            self.entry_lyt.addWidget(self.entries[i])

    def update_fields(self) -> None:
        """
        Update entry widgets to previously entered values
        """
        self.event_type_entry.setCurrentText(self.db.event_type)
        self.location_entry.setCurrentText(self.db.location)
        self.scheme_lifetime_entry.setValue(self.db.scheme_lifetime)
        self.sop_entry.setValue(self.db.sop)
        self.evac_cost_entry.setCurrentText(self.db.evac_cost_category)
        self.cellar_entry.setChecked(self.db.cellar)
        self.res_cap_entry.setText(str(self.db.res_cap))
        self.non_res_cap_entry.setText(str(self.db.non_res_cap))
        self.cap_enabled_entry.setChecked(self.db.caps_enabled)

    def enable_cap(self) -> None:
        """
        Enable/Disable cap labels and entries based on checkbutton state
        """
        if self.db.caps_enabled:
            self.res_cap_label.setDisabled(True)
            self.res_cap_entry.setDisabled(True)
            self.non_res_cap_label.setDisabled(True)
            self.non_res_cap_entry.setDisabled(True)

        else:
            self.res_cap_label.setEnabled(True)
            self.res_cap_entry.setEnabled(True)
            self.non_res_cap_label.setEnabled(True)
            self.non_res_cap_entry.setEnabled(True)

        self.db.caps_enabled = not self.db.caps_enabled

    def add_fe(self) -> None:
        """
        Add flood event and corresponding spinbox
        """
        # Add fe
        self.db.return_periods.append(1)

        # Reload display
        self.build_lyt()

    def remove_fe(self) -> None:
        """
        Remove flood event and corresponding spinbox
        """
        # Don't remove last entry
        if len(self.entries) > 1:

            # Remove fe
            del self.db.return_periods[-1]

        # Reload display
        self.build_lyt()

    def update_fe(self) -> None:
        """
        Disable flood events editing if properties have been uploaded
        """
        if self.db.node_count != 0:
            self.fe_group.setDisabled(True)

            warning = QLabel(
                "Flood event nodes have already been added so flood events cannot be changed")
            warning.setWordWrap(True)
            warning.setAlignment(Qt.AlignCenter)

            self.main_lyt.addWidget(warning, 3, 1, 1, 1)


class DamagesBreakdown(QDialog):
    def __init__(self, parent: ResultsTab, db: DetailedDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Display fields
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.capping_label = QLabel(
            "Damage Capping is Enabled and so some depths may have been capped")

        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.parent.frameGeometry().size())

        self.initUI()
        self.residential_breakdown()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel(
            "Here you can view a property-by-property breakdown of damages calculated in this appraisal")
        text.setAlignment(Qt.AlignCenter)

        res_btn = QPushButton("Residential")
        res_btn.clicked.connect(self.residential_breakdown)
        non_res_btn = QPushButton("Non-Residential")
        non_res_btn.clicked.connect(self.non_residential_breakdown)
        intangible_btn = QPushButton("Intangible")
        intangible_btn.clicked.connect(self.intangible_breakdown)
        mh_btn = QPushButton("Mental Health")
        mh_btn.clicked.connect(self.mental_health_breakdown)
        vehicle_btn = QPushButton("Vehicle")
        vehicle_btn.clicked.connect(self.vehicle_breakdown)
        evac_btn = QPushButton("Evacuation")
        evac_btn.clicked.connect(self.evac_breakdown)

        self.capping_label.setAlignment(Qt.AlignCenter)

        btn_lyt = QHBoxLayout()
        btn_lyt.addWidget(res_btn)
        btn_lyt.addWidget(non_res_btn)
        btn_lyt.addWidget(intangible_btn)
        btn_lyt.addWidget(mh_btn)
        btn_lyt.addWidget(vehicle_btn)
        btn_lyt.addWidget(evac_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setDefault(True)
        close_btn.setFocus()

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt))
        main_lyt.addWidget(self.table)
        main_lyt.addWidget(self.capping_label)
        self.capping_label.hide()
        main_lyt.addLayout(utils.centered_hbox(close_btn))
        self.setLayout(main_lyt)

    def residential_breakdown(self) -> None:
        """
        Display breakdown of residential damages
        """
        # Generate table headings and set table size
        col_headings = ["Address", "Average\nAnnual Damage", "Lifetime Damage"]
        if self.db.caps_enabled:
            col_headings += ["Capped Average\nAnnual Damage",
                             "Capped\nLifetime Damage"]

        # Offset used for placement of depth and damage data
        offset = len(col_headings)

        col_headings += ["AEP: {}%".format(round(100/rp, 2))
                         for rp in self.db.return_periods]
        row_headings = ["Depth (m)", "Damage (£)"] * self.db.clean_res_count
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        if self.db.caps_enabled:
            # Display capped data if available
            for i in range(self.db.clean_res_count):
                # Capped average annual damage
                capped_average_item = QTableWidgetItem(
                    str(round(self.db.capped_average_annual_damage_per_res[i], 2)))
                self.table.setSpan(i*2, 3, 2, 1)
                self.table.setItem(i*2, 3, capped_average_item)

                # Capped lifetime damage
                capped_lifetime_item = QTableWidgetItem(
                    str(round(self.db.capped_lifetime_damage_per_res[i], 2)))
                self.table.setSpan(i*2, 4, 2, 1)
                self.table.setItem(i*2, 4, capped_lifetime_item)

        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setSpan(i*2, 0, 2, 1)
            self.table.setItem(i*2, 0, address_item)

            # Average annual damage
            average_damage_item = QTableWidgetItem(
                str(round(self.db.average_annual_damage_per_res[i], 2)))
            self.table.setSpan(i*2, 1, 2, 1)
            self.table.setItem(i*2, 1, average_damage_item)

            # Lifetime damage
            lifetime_damage_item = QTableWidgetItem(
                str(round(self.db.lifetime_damage_per_res[i], 2)))
            self.table.setSpan(i*2, 2, 2, 1)
            self.table.setItem(i*2, 2, lifetime_damage_item)

            for event in range(len(self.db.return_periods)):
                depth_item = QTableWidgetItem(
                    str(round(self.db.res_depths[i][event], 5)))
                damage_item = QTableWidgetItem(
                    str(round(self.db.res_damages[i][event], 2)))
                self.table.setItem(i*2, offset+event, depth_item)
                self.table.setItem(i*2 + 1, offset+event, damage_item)

        # Capping label
        if self.db.caps_enabled:
            self.capping_label.show()
        else:
            self.capping_label.hide()

    def non_residential_breakdown(self) -> None:
        """
        Display breakdown of non-residential damages
        """
        # Generate table headings and set table size
        col_headings = ["Address", "Average\nAnnual Damage", "Lifetime Damage"]
        if self.db.caps_enabled:
            col_headings += [
                "Capped Average\nAnnual Damage", "Capped\nLifetime Damage"]

        col_headings += ["Floor Area (m²)"]

        # Offset used for placement of depth and damage data
        offset = len(col_headings)

        col_headings += ["AEP: {}%".format(round(100/rp, 2))
                         for rp in self.db.return_periods]
        row_headings = ["Depth (m)", "Damage (£)"] * \
            self.db.clean_non_res_count
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Popuplate table
        if self.db.caps_enabled:
            # Display capped data if available
            for i in range(self.db.clean_non_res_count):
                # Capped average annual damage
                capped_average_item = QTableWidgetItem(
                    str(round(self.db.capped_average_annual_damage_per_non_res[i], 2)))
                self.table.setSpan(i*2, 3, 2, 1)
                self.table.setItem(i*2, 3, capped_average_item)

                # Capped lifetime damage
                capped_lifetime_item = QTableWidgetItem(
                    str(round(self.db.capped_lifetime_damage_per_non_res[i], 2)))
                self.table.setSpan(i*2, 4, 2, 1)
                self.table.setItem(i*2, 4, capped_lifetime_item)

        for i in range(self.db.clean_non_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_non_res_a[i])
            self.table.setSpan(i*2, 0, 2, 1)
            self.table.setItem(i*2, 0, address_item)

            # Average annual damage
            average_damage_item = QTableWidgetItem(
                str(round(self.db.average_annual_damage_per_non_res[i], 2)))
            self.table.setSpan(i*2, 1, 2, 1)
            self.table.setItem(i*2, 1, average_damage_item)

            # Lifetime damage
            lifetime_damage_item = QTableWidgetItem(
                str(round(self.db.lifetime_damage_per_non_res[i], 2)))
            self.table.setSpan(i*2, 2, 2, 1)
            self.table.setItem(i*2, 2, lifetime_damage_item)

            # Floor area
            floor_area_item = QTableWidgetItem(
                str(round(self.db.clean_non_res_fa[i], 2)))
            self.table.setSpan(i*2, offset-1, 2, 1)
            self.table.setItem(i*2, offset-1, floor_area_item)

            for event in range(len(self.db.return_periods)):
                depth_item = QTableWidgetItem(
                    str(round(self.db.non_res_depths[i][event], 5)))
                damage_item = QTableWidgetItem(
                    str(round(self.db.non_res_damages[i][event], 2)))
                self.table.setItem(i*2, offset+event, depth_item)
                self.table.setItem(i*2 + 1, offset+event, damage_item)

        # Capping label
        if self.db.caps_enabled:
            self.capping_label.show()
        else:
            self.capping_label.hide()

    def intangible_breakdown(self) -> None:
        """
        Display breakdown of intangible damages
        """
        # Generate table headings and set table size
        col_headings = [
            "Address", "Current SOP\n(AEP %)", "Average\nAnnual Damage", "Lifetime Damage"]
        row_headings = ["Damage (£)"] * self.db.clean_res_count
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setSpan(i, 0, 1, 1)
            self.table.setItem(i, 0, address_item)

            # Current sop
            sop_item = QTableWidgetItem(
                str(round(self.db.current_sops[i], 2)) if self.db.current_sops[i] else "None")
            self.table.setSpan(i, 1, 1, 1)
            self.table.setItem(i, 1, sop_item)

            # Average annual damage
            average_damage_item = QTableWidgetItem(
                str(round(self.db.average_annual_intangible_damages[i], 2)))
            self.table.setSpan(i, 2, 1, 1)
            self.table.setItem(i, 2, average_damage_item)

            # Lifetime damage
            lifetime_damage_item = QTableWidgetItem(
                str(round(self.db.lifetime_intangible_damages[i], 2)))
            self.table.setSpan(i, 3, 1, 1)
            self.table.setItem(i, 3, lifetime_damage_item)

        # Capping label
        if self.db.caps_enabled:
            self.capping_label.show()
        else:
            self.capping_label.hide()

    def mental_health_breakdown(self) -> None:
        """
        Display breakdown of mental health damages
        """
        # Generate table headings and set table size
        col_headings = ["Address", "Average\nAnnual Damage", "Lifetime Damage"]

        # Offset used for placement of depth and damage data
        offset = len(col_headings)

        col_headings += ["AEP: {}%".format(round(100/rp, 2))
                         for rp in self.db.return_periods]
        row_headings = ["Depth (m)", "Damage (£)"] * self.db.clean_res_count
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setSpan(i*2, 0, 2, 1)
            self.table.setItem(i*2, 0, address_item)

            # Average annual damage
            average_damage_item = QTableWidgetItem(
                str(round(self.db.average_annual_mh_costs[i], 2)))
            self.table.setSpan(i*2, 1, 2, 1)
            self.table.setItem(i*2, 1, average_damage_item)

            # Lifetime damage
            lifetime_damage_item = QTableWidgetItem(
                str(round(self.db.lifetime_mh_costs[i], 2)))
            self.table.setSpan(i*2, 2, 2, 1)
            self.table.setItem(i*2, 2, lifetime_damage_item)

            for event in range(len(self.db.return_periods)):
                depth_item = QTableWidgetItem(
                    str(round(self.db.capped_res_depths[i][event], 5)))
                damage_item = QTableWidgetItem(
                    str(round(self.db.mh_costs[i][event], 2)))
                self.table.setItem(i*2, offset+event, depth_item)
                self.table.setItem(i*2 + 1, offset+event, damage_item)

        # Capping label
        if self.db.caps_enabled:
            self.capping_label.show()
        else:
            self.capping_label.hide()

    def vehicle_breakdown(self) -> None:
        """
        Display breakdown of vehicular damages
        """
        # Generate table headings and set table size
        col_headings = ["Address", "Average\nAnnual Damage", "Lifetime Damage"]

        # Offset used for placement of depth and damage data
        offset = len(col_headings)

        col_headings += ["AEP: {}%".format(round(100/rp, 2))
                         for rp in self.db.return_periods]
        row_headings = ["Depth (m)", "Damage (£)"] * self.db.clean_res_count
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setSpan(i*2, 0, 2, 1)
            self.table.setItem(i*2, 0, address_item)

            # Average annual damage
            average_damage_item = QTableWidgetItem(
                str(round(self.db.average_annual_vehicular_damages[i], 2)))
            self.table.setSpan(i*2, 1, 2, 1)
            self.table.setItem(i*2, 1, average_damage_item)

            # Lifetime damage
            lifetime_damage_item = QTableWidgetItem(
                str(round(self.db.lifetime_vehicular_damages[i], 2)))
            self.table.setSpan(i*2, 2, 2, 1)
            self.table.setItem(i*2, 2, lifetime_damage_item)

            for event in range(len(self.db.return_periods)):
                depth_item = QTableWidgetItem(
                    str(round(self.db.capped_res_depths[i][event], 5)))
                damage_item = QTableWidgetItem(
                    str(round(self.db.vehicular_damages[i][event], 2)))
                self.table.setItem(i*2, offset+event, depth_item)
                self.table.setItem(i*2 + 1, offset+event, damage_item)

        # Capping label
        if self.db.caps_enabled:
            self.capping_label.show()
        else:
            self.capping_label.hide()

    def evac_breakdown(self) -> None:
        """
        Display breakdown of vehicular damages
        """
        # Generate table headings and set table size
        col_headings = ["Address", "Average\nAnnual Damage", "Lifetime Damage"]

        # Offset used for placement of depth and damage data
        offset = len(col_headings)

        col_headings += ["AEP: {}%".format(round(100/rp, 2))
                         for rp in self.db.return_periods]
        row_headings = ["Depth (m)", "Damage (£)"] * self.db.clean_res_count
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setSpan(i*2, 0, 2, 1)
            self.table.setItem(i*2, 0, address_item)

            # Average annual damage
            average_damage_item = QTableWidgetItem(
                str(round(self.db.average_annual_evac_costs[i], 2)))
            self.table.setSpan(i*2, 1, 2, 1)
            self.table.setItem(i*2, 1, average_damage_item)

            # Lifetime damage
            lifetime_damage_item = QTableWidgetItem(
                str(round(self.db.lifetime_evac_costs[i], 2)))
            self.table.setSpan(i*2, 2, 2, 1)
            self.table.setItem(i*2, 2, lifetime_damage_item)

            for event in range(len(self.db.return_periods)):
                depth_item = QTableWidgetItem(
                    str(round(self.db.capped_res_depths[i][event], 5)))
                damage_item = QTableWidgetItem(
                    str(round(self.db.evac_costs[i][event], 2)))
                self.table.setItem(i*2, offset+event, depth_item)
                self.table.setItem(i*2 + 1, offset+event, damage_item)

        # Capping label
        if self.db.caps_enabled:
            self.capping_label.show()
        else:
            self.capping_label.hide()


class BenefitsBreakdown(QDialog):
    def __init__(self, parent: ResultsTab, db: DetailedDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Display fields
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.label_1 = QLabel()
        self.label_2 = QLabel()
        self.capping_label = QLabel()

        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.parent.frameGeometry().size())

        self.initUI()
        self.residential_breakdown()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel(
            "Here you can view a property-by-property breakdown of benefits calculated in this appraisal")
        text.setAlignment(Qt.AlignCenter)

        res_btn = QPushButton("Residential")
        res_btn.clicked.connect(self.residential_breakdown)
        non_res_btn = QPushButton("Non-Residential")
        non_res_btn.clicked.connect(self.non_residential_breakdown)
        intangible_btn = QPushButton("Intangible")
        intangible_btn.clicked.connect(self.intangible_breakdown)
        mh_btn = QPushButton("Mental Health")
        mh_btn.clicked.connect(self.mental_health_breakdown)
        vehicle_btn = QPushButton("Vehicle")
        vehicle_btn.clicked.connect(self.vehicle_breakdown)
        evac_btn = QPushButton("Evacuation")
        evac_btn.clicked.connect(self.evac_breakdown)

        btn_lyt = QHBoxLayout()
        btn_lyt.addWidget(res_btn)
        btn_lyt.addWidget(non_res_btn)
        btn_lyt.addWidget(intangible_btn)
        btn_lyt.addWidget(mh_btn)
        btn_lyt.addWidget(vehicle_btn)
        btn_lyt.addWidget(evac_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setDefault(True)
        close_btn.setFocus()

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt))
        main_lyt.addWidget(self.table)
        main_lyt.addWidget(self.label_1)
        main_lyt.addWidget(self.label_2)
        main_lyt.addWidget(self.capping_label)
        self.label_1.hide()
        self.label_2.hide()
        self.capping_label.hide()
        main_lyt.addLayout(utils.centered_hbox(close_btn))
        self.setLayout(main_lyt)

    def residential_breakdown(self) -> None:
        """
        Display breakdown of residential benefits
        """
        # Generate table headings and set table size
        # Ignore first return period becuase of how benefit trapezia are calculated
        col_headings = [
            "Address"] + ["AEP: {}%".format(round(100/rp, 2)) for rp in self.db.return_periods[1::]]
        row_headings = ["Residential Property {}".format(i) for i in range(
            self.db.clean_res_count)] + ["Total Residential Benefit"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        # Some ranges are decremented becuase of how benefit trapezia are calculated
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setItem(i, 0, address_item)

            for event in range(len(self.db.return_periods) - 1):
                benefit_item = QTableWidgetItem(
                    str(round(self.db.res_benefits[i][event], 2)))
                self.table.setItem(i, event+1, benefit_item)

        # Totals
        for event in range(len(self.db.return_periods) - 1):
            total_item = QTableWidgetItem(
                str(round(self.db.total_res_benefits[event], 2)))
            self.table.setItem(self.db.clean_res_count, event+1, total_item)

    def non_residential_breakdown(self) -> None:
        """
        Display breakdown of non-residential benefits
        """
        # Generate table headings and set table size
        # Ignore first return period because of how benefit trapezia are calculated
        col_headings = [
            "Address"] + ["AEP: {}%".format(round(100/rp, 2)) for rp in self.db.return_periods[1::]]
        row_headings = ["Non-residential Property {}".format(i) for i in range(
            self.db.clean_non_res_count)] + ["Total Non-residential Benefit"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        # Some ranges are decremented because of how benefit trapezia are calculated
        for i in range(self.db.clean_non_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_non_res_a[i])
            self.table.setItem(i, 0, address_item)

            for event in range(len(self.db.return_periods) - 1):
                benefit_item = QTableWidgetItem(
                    str(round(self.db.non_res_benefits[i][event], 2)))
                self.table.setItem(i, event+1, benefit_item)

        # Totals
        for event in range(len(self.db.return_periods) - 1):
            total_item = QTableWidgetItem(
                str(round(self.db.total_non_res_benefits[event], 2)))
            self.table.setItem(self.db.clean_non_res_count,
                               event+1, total_item)

    def intangible_breakdown(self) -> None:
        """
        Display breakdown of intangible benefits
        """
        # Generate table headings and set table size
        col_headings = ["Address",
                        "Average Annual\nBenefit (£)", "Lifetime\nBenefit (£)"]
        row_headings = ["Residential Property {}".format(
            i) for i in range(self.db.clean_res_count)]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setItem(i, 0, address_item)

            # Average annual benefit
            annual_item = QTableWidgetItem(
                str(round(self.db.annual_intangible_benefits[i], 2)))
            self.table.setItem(i, 1, annual_item)

            # Lifetime benefit
            lifetime_item = QTableWidgetItem(
                str(round(self.db.lifetime_intangible_benefits[i], 2)))
            self.table.setItem(i, 2, lifetime_item)

        # Totals
        total_annual_item = QTableWidgetItem(
            str(round(self.db.current_annual_intangible_benefit, 2)))
        self.table.setItem(self.db.clean_res_count, 1, total_annual_item)

        total_lifetime_item = QTableWidgetItem(
            str(round(self.db.current_lifetime_intangible_benefit, 2)))
        self.table.setItem(self.db.clean_res_count, 2, total_lifetime_item)

    def mental_health_breakdown(self) -> None:
        """
        Display breakdown of mental health benefits
        """
        # Generate table headings and set table size
        # Ignore first return period because of how benefit trapezia are calculated
        col_headings = [
            "Address"] + ["AEP: {}%".format(round(100/rp, 2)) for rp in self.db.return_periods[1::]]
        row_headings = ["Residential Property {}".format(i) for i in range(
            self.db.clean_res_count)] + ["Total Mental Health Benefit"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        # Some ranges are decremented because of how benefit trapezia are calculated
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setItem(i, 0, address_item)

            for event in range(len(self.db.return_periods) - 1):
                benefit_item = QTableWidgetItem(
                    str(round(self.db.mh_benefits[i][event], 2)))
                self.table.setItem(i, event+1, benefit_item)

        # Totals
        for event in range(len(self.db.return_periods) - 1):
            total_item = QTableWidgetItem(
                str(round(self.db.total_mh_benefits[event], 2)))
            self.table.setItem(self.db.clean_res_count, event+1, total_item)

    def vehicle_breakdown(self) -> None:
        """
        Display breakdown of vehicle benefits
        """
        # Generate table headings and set table size
        # Ignore first return period becuase of how benefit trapezia are calculated
        col_headings = [
            "Address"] + ["AEP: {}%".format(round(100/rp, 2)) for rp in self.db.return_periods[1::]]
        row_headings = ["Residential Property {}".format(i) for i in range(
            self.db.clean_res_count)] + ["Total Vehicle Benefit"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        # Some ranges are decremented because of how benefit trapezia are calculated
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setItem(i, 0, address_item)

            for event in range(len(self.db.return_periods) - 1):
                benefit_item = QTableWidgetItem(
                    str(round(self.db.vehicular_benefits[i][event], 2)))
                self.table.setItem(i, event+1, benefit_item)

        # Totals
        for event in range(len(self.db.return_periods) - 1):
            total_item = QTableWidgetItem(
                str(round(self.db.total_vehicular_benefits[event], 2)))
            self.table.setItem(self.db.clean_res_count, event+1, total_item)

    def evac_breakdown(self) -> None:
        """
        Display breakdown of evac benefits
        """
        # Generaet table headings and set table size
        # Ignore first return period because of how benefit trapezia are calculated
        col_headings = [
            "Adress"] + ["AEP: {}%".format(round(100/rp, 2)) for rp in self.db.return_periods[1::]]
        row_headings = ["Residential Property {}".format(i) for i in range(
            self.db.clean_res_count)] + ["Total Evacuation Benefit"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        # Some ranges are decremented because of how benefit trapezia are calculated
        for i in range(self.db.clean_res_count):
            # Address
            address_item = QTableWidgetItem(self.db.clean_res_a[i])
            self.table.setItem(i, 0, address_item)

            for event in range(len(self.db.return_periods) - 1):
                benefit_item = QTableWidgetItem(
                    str(round(self.db.evac_benefits[i][event], 2)))
                self.table.setItem(i, event+1, benefit_item)

        # Totals
        for event in range(len(self.db.return_periods) - 1):
            total_item = QTableWidgetItem(
                str(round(self.db.total_evac_benefits[event], 2)))
            self.table.setItem(self.db.clean_res_count, event+1, total_item)


class ExportResults(QDialog):
    def __init__(self, parent: ResultsTab) -> None:
        super().__init__(parent)
        self.parent = parent

        # Display fields
        breakdown_options = [
            "Residential",
            "Intangible",
            "Mental Health",
            "Vehicular",
            "Evacuation",
            "Non-Residential"
        ]
        self.damage_btns = [QCheckBox(option) for option in breakdown_options]
        self.benefit_btns = [QCheckBox(option) for option in breakdown_options]
        file_options = [
            ".csv",
            ".xlsx"
        ]
        self.file_btns = [QCheckBox(option) for option in file_options]

        # Save location
        self.path = ""

        self.setWindowModality(Qt.WindowModal)
        self.initUI()

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel("Select the data you would like to export")
        text.setAlignment(Qt.AlignCenter)

        # Damages Groupbox
        damages_lyt = QVBoxLayout()
        damages_lyt.setSpacing(10)
        for btn in self.damage_btns:
            damages_lyt.addWidget(btn)
        damages_group = QGroupBox("Damage Breakdowns")
        damages_group.setLayout(damages_lyt)

        # Benefits Groupbox
        benefits_lyt = QVBoxLayout()
        benefits_lyt.setSpacing(10)
        for btn in self.benefit_btns:
            benefits_lyt.addWidget(btn)
        benefits_group = QGroupBox("Benefit Breakdowns")
        benefits_group.setLayout(benefits_lyt)

        # File formats Groupbox
        file_format_lyt = QHBoxLayout()
        for btn in self.file_btns:
            file_format_lyt.addLayout(utils.centered_hbox(btn))
        file_format_group = QGroupBox("File Formats")
        file_format_group.setLayout(file_format_lyt)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.check_entries)

        main_lyt = QGridLayout()
        main_lyt.setSpacing(25)
        main_lyt.addWidget(text, 0, 0, 1, 2)
        main_lyt.addWidget(damages_group, 1, 0, 1, 1)
        main_lyt.addWidget(benefits_group, 1, 1, 1, 1)
        main_lyt.addWidget(file_format_group, 2, 0, 1, 2)
        main_lyt.addLayout(utils.centered_hbox(export_btn), 3, 0, 1, 2)
        self.setLayout(main_lyt)

    def check_entries(self) -> None:
        """
        Check at least one file format is selected
        """
        if sum([btn.isChecked() for btn in self.file_btns]):
            # At least one button selected
            self.get_file_path()

        else:
            # No file formats selected
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("Please select at least one file format")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setEscapeButton(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.exec_()

    def get_file_path(self) -> None:
        """
        Ask for save location
        """
        # Discard filetype from fname
        self.path = utils.get_save_fname(self)

        # Location selected
        if self.path:
            self.accept()


"""
####################
### MULTIHREADING ##
####################
"""


class JSONWriteWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, appraisal: DetailedAppraisal, fname: str) -> None:
        super().__init__()
        self.appraisal = appraisal
        self.fname = fname

    def run(self) -> None:
        """
        Long-running JSON-writing task
        """
        try:
            with open(f"{self.fname}.trit", "w") as f:
                json.dump(self.appraisal.db.__dict__,
                          f, cls=utils.NumpyEncoder)

        except Exception as e:
            self.error.emit(e)

            # Delete half-written results file
            if os.path.exists(f"{self.fname}.trit"):
                os.remove(f"{self.fname}.trit")

        # Execution finished
        self.finished.emit()


class JSONLoadWorker(QObject):
    # Signal fields
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, appraisal: DetailedAppraisal, fname: str) -> None:
        super().__init__()
        self.appraisal = appraisal
        self.fname = fname

    def run(self) -> None:
        """
        Long-running JSON-loading task 
        """
        try:
            with open(self.fname, "r") as f:
                self.appraisal.db.__dict__ = json.load(f)

        except Exception as e:
            self.error.emit(e)

        # Execution finished
        self.finished.emit()


class AsciiWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    progress = pyqtSignal(float)
    error = pyqtSignal(Exception, str)

    def __init__(self, appraisal: DetailedAppraisal, fnames: List[str]) -> None:
        super().__init__()
        self.appraisal = appraisal
        self.fnames = fnames

    def run(self) -> None:
        """
        Long-running ASCII upload task
        """
        ascii_count = len(self.fnames)

        try:
            for i in range(ascii_count):
                self.appraisal.db.add_ascii(self.fnames[i])
                # Progress signal
                self.progress.emit(i/ascii_count)

        except Exception as e:
            self.error.emit(e, self.fnames[i])

        # Execution finished
        self.finished.emit()


class PropUploadWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    progress = pyqtSignal(float)
    error = pyqtSignal(Exception)

    def __init__(self, appraisal: DetailedAppraisal, columns: List[int], table: QTableWidget) -> None:
        super().__init__()
        self.appraisal = appraisal
        self.columns = columns
        self.table = table

    def run(self) -> None:
        """
        Long-running property upload task
        """
        try:
            props = utils.read_table_with_columns(self.columns, self.table)
            prop_count = len(props)
            for i in range(prop_count):
                self.appraisal.db.add_prop(props[i])
                # Progress signal
                self.progress.emit(i/prop_count)

        except Exception as e:
            self.error.emit(e)

        # Execution finished
        self.finished.emit()


class NodeUploadWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    progress = pyqtSignal(float)
    error = pyqtSignal(Exception)

    def __init__(self, appraisal: DetailedAppraisal, columns: List[int], table: QTableWidget) -> None:
        super().__init__()
        self.appraisal = appraisal
        self.columns = columns
        self.table = table

    def run(self) -> None:
        """
        Long-running node-upload task
        """
        try:
            nodes = utils.read_table_with_columns(self.columns, self.table)
            node_count = len(nodes)
            for i in range(node_count):
                self.appraisal.db.add_node(nodes[i])
                # Progress signal
                self.progress.emit(i/node_count)

        except Exception as e:
            self.error.emit(e)

        # Execution finished
        self.finished.emit()
