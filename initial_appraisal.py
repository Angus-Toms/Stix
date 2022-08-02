"""
UI widget for initial appraisals performed by Triton FAS

Angus Toms
14 06 2021
"""
import json
import os

from PyQt5.QtCore import (QObject, Qt, QThread, pyqtSignal)
from PyQt5.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDialog, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QMessageBox, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

import utils
import const
from initial_datahandler import InitialDataHandler


class InitialAppraisal(QWidget):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

        self.db = InitialDataHandler()

        # Connect MenuBar actions
        self.controller.save_action.disconnect()
        self.controller.export_action.disconnect()
        self.controller.save_action.triggered.connect(self.save_results)
        self.controller.export_action.triggered.connect(self.export_results)

        # Display fields
        self.prop_count_label = QLabel()
        self.warning_label = QLabel()
        self.scheme_lifetime_label = QLabel()
        self.location_label = QLabel()
        self.sop_label = QLabel()
        self.table = QTableWidget()

        self.save_results_btn = QPushButton("Save Appraisal")
        self.main_lyt = QGridLayout()

        self.initUI()
        self.update_event_details()
        self.update_table()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel(
            "From here you can edit flood information,  generate,  and export results")
        text.setAlignment(Qt.AlignCenter)

        # Event details groupbox
        self.prop_count_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.scheme_lifetime_label.setAlignment(Qt.AlignCenter)
        self.location_label.setAlignment(Qt.AlignCenter)
        self.sop_label.setAlignment(Qt.AlignCenter)
        edit_btn = QPushButton("Edit Flood Event Details")
        edit_btn.clicked.connect(self.edit_event_details)

        details_lyt = QVBoxLayout()
        details_lyt.addStretch()
        details_lyt.addWidget(self.prop_count_label)
        details_lyt.addWidget(self.scheme_lifetime_label)
        details_lyt.addWidget(self.sop_label)
        details_lyt.addWidget(self.warning_label)
        details_lyt.addWidget(self.location_label)
        details_lyt.addLayout(utils.centered_hbox(edit_btn))
        details_lyt.addStretch()
        details_group = QGroupBox("Flood Event Details")
        details_group.setLayout(details_lyt)

        # Table setup and results groupbox
        col_headings = ["Properties at risk",
                        "Lower Annual Damage (£)", "Upper Annual Damage (£)"]
        row_headings = const.initial_aeps + [None, None, None, None]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        get_results_btn = QPushButton("Generate Results")
        get_results_btn.clicked.connect(self.get_results)

        results_lyt = QVBoxLayout()
        results_lyt.addWidget(self.table)
        results_lyt.addLayout(utils.centered_hbox(get_results_btn))
        results_group = QGroupBox("Results")
        results_group.setLayout(results_lyt)

        # Advanced groupbox
        view_breakdown_btn = QPushButton("View Breakdown")
        view_breakdown_btn.clicked.connect(self.view_breakdown)
        export_results_btn = QPushButton("Export Results")
        export_results_btn.clicked.connect(self.export_results)
        self.save_results_btn.clicked.connect(self.save_results)

        advanced_lyt = QHBoxLayout()
        advanced_lyt.addStretch()
        advanced_lyt.addWidget(view_breakdown_btn)
        advanced_lyt.addStretch()
        advanced_lyt.addWidget(export_results_btn)
        advanced_lyt.addStretch()
        advanced_lyt.addWidget(self.save_results_btn)
        advanced_lyt.addStretch()

        advanced_group = QGroupBox("Advanced")
        advanced_group.setLayout(advanced_lyt)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.return_home)

        self.main_lyt.setColumnStretch(0, 1)
        self.main_lyt.setColumnStretch(1, 2)
        self.main_lyt.addWidget(text, 0, 0, 1, 2)
        self.main_lyt.addWidget(details_group, 1, 0, 1, 1)
        self.main_lyt.addWidget(results_group, 1, 1, 1, 1)
        self.main_lyt.addWidget(advanced_group, 2, 0, 1, 2)
        self.main_lyt.addLayout(utils.centered_hbox(home_btn), 4, 0, 1, 2)
        self.setLayout(self.main_lyt)

    def return_home(self) -> None:
        """
        Leave initial appraisal widget
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

    def view_breakdown(self) -> None:
        """
        Run the ResultsBreakdown dialog
        """
        popup = ResultsBreakdown(self, self.db)
        popup.exec_()

    def export_results(self) -> None:
        """
        Run the ExportResults dialog
        """
        popup = ExportResults(self)

        if popup.exec_():
            # Save button pressed
            try:
                fname = popup.path
                datapoint_options = [btn.isChecked()
                                     for btn in popup.export_btns]
                file_formats = [btn.isChecked() for btn in popup.file_btns]

                # Write files
                self.db.export_results(fname, datapoint_options, file_formats)
                utils.write_method_caveats(
                    "initial", os.path.join(fname, "Notes"))

            except Exception as e:
                msgbox = QMessageBox(self)
                msgbox.setIcon(QMessageBox.Warning)
                msgbox.setText(
                    "An error occured during the export of these results")
                msgbox.setDetailedText(e)
                msgbox.setStandardButtons(QMessageBox.Ok)
                msgbox.exec_()

    def get_results(self) -> None:
        """
        Generate results for currently uploaded flood information
        """
        # Update results fields
        self.db.get_results()

        # Update displays
        self.update_table()

    def edit_event_details(self) -> None:
        """
        Run the EditFloodDetails dialog
        """
        popup = EditFloodDetails(self, self.db)

        if popup.exec_():
            # Save general flood information
            self.db.prop_count = int(popup.prop_count_entry.text())
            self.db.warning = popup.warning_entry.currentText()
            self.db.scheme_lifetime = int(popup.scheme_lifetime_entry.text())
            self.db.location = popup.location_entry.currentText()
            self.db.sop = int(popup.sop_entry.text())

            # Update display
            self.update_event_details()

    def update_event_details(self) -> None:
        """
        Reload display of flood information labels
        """
        self.prop_count_label.setText(
            "Properties in FZ3: {}".format(self.db.prop_count))
        self.warning_label.setText("Flood Warning: {}".format(self.db.warning))
        self.scheme_lifetime_label.setText(
            "Scheme Lifetime: {} years".format(self.db.scheme_lifetime))
        self.location_label.setText("Location: {}".format(self.db.location))
        self.sop_label.setText(
            "Standard of Protection: {} years".format(self.db.sop))

    def update_table(self) -> None:
        """
        Update display of self.table
        """
        datapoints = self.db.get_major_datapoints()
        for row in range(len(datapoints)):
            for col in range(len(datapoints[0])):

                # Format numerical entries
                try:
                    item = QTableWidgetItem(
                        "{:,.2f}".format(datapoints[row][col]))
                    self.table.setItem(row, col, item)

                except (ValueError, TypeError):
                    item = QTableWidgetItem(datapoints[row][col])
                    self.table.setItem(row, col, item)

    def save_results(self) -> None:
        """
        Save appraisal to .trit file
        """
        fname = utils.get_save_fname(self)

        if fname:
            # Only run if file is selected
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

            # Reload diplsays upon task finishing
            self.thread.finished.connect(self.update_event_details)
            self.thread.finished.connect(self.update_table)

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
##### DIALOGS ######
####################
"""


class EditFloodDetails(QDialog):
    def __init__(self, parent: InitialAppraisal, db: InitialDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Entry fields
        self.prop_count_entry = QSpinBox()
        self.warning_entry = QComboBox()
        self.scheme_lifetime_entry = QSpinBox()
        self.location_entry = QComboBox()
        self.sop_entry = QSpinBox()

        self.setWindowModality(Qt.WindowModal)
        self.initUI()
        self.update_fields()

        # Disable resizing
        self.setFixedSize(self.sizeHint())

    def initUI(self) -> None:
        """
        UI Setup 
        """
        text = QLabel("Edit General Flood Information below")
        text.setAlignment(Qt.AlignCenter)

        prop_count_label = QLabel("Number of properties within FZ3")
        warning_label = QLabel("Flood Warning")
        scheme_lifetime_label = QLabel("Scheme Lifetime")
        location_label = QLabel("Location Type")
        sop_label = QLabel("Standard of Protection")

        warnings = [
            "No Warning",
            "Less than 8 hours",
            "More than 8 hours"
        ]
        self.warning_entry.addItems(warnings)
        location_types = [
            "Rural",
            "Urban"
        ]
        self.location_entry.addItems(location_types)
        self.prop_count_entry.setMinimum(1)
        self.prop_count_entry.setMaximum(10000)
        self.scheme_lifetime_entry.setMinimum(1)
        self.scheme_lifetime_entry.setMaximum(100)
        self.sop_entry.setMinimum(1)
        self.sop_entry.setMaximum(200)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        save_btn.setFocus()
        btn_lyt = QHBoxLayout()
        btn_lyt.addWidget(cancel_btn)
        btn_lyt.addWidget(save_btn)

        form = QFormLayout()
        form.addRow(prop_count_label, self.prop_count_entry)
        form.addRow(scheme_lifetime_label, self.scheme_lifetime_entry)
        form.addRow(sop_label, self.sop_entry)
        form.addRow(warning_label, self.warning_entry)
        form.addRow(location_label, self.location_entry)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(10)
        main_lyt.addWidget(text)
        main_lyt.addLayout(form)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt))
        self.setLayout(main_lyt)

    def update_fields(self) -> None:
        """
        Update entry widgets to previously entered values
        """
        self.prop_count_entry.setValue(self.db.prop_count)
        self.warning_entry.setCurrentText(self.db.warning)
        self.scheme_lifetime_entry.setValue(self.db.scheme_lifetime)
        self.location_entry.setCurrentText(self.db.location)
        self.sop_entry.setValue(self.db.sop)


class ResultsBreakdown(QDialog):
    def __init__(self, parent: InitialAppraisal, db: InitialDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Display fields
        self.table = QTableWidget()

        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.frameGeometry().size())

        self.initUI()
        self.property_count_breakdown()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel(
            "Here you can view a more advanced breakdown of appraisal results")
        text.setAlignment(Qt.AlignCenter)

        prop_count_btn = QPushButton("Property Counts")
        prop_count_btn.clicked.connect(self.property_count_breakdown)
        existing_damages_btn = QPushButton("Existing Damages")
        existing_damages_btn.clicked.connect(self.existing_damages_breakdown)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        btn_lyt = QHBoxLayout()
        btn_lyt.addWidget(prop_count_btn)
        btn_lyt.addWidget(existing_damages_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt))
        main_lyt.addWidget(self.table)
        main_lyt.addLayout(utils.centered_hbox(close_btn))
        self.setLayout(main_lyt)

    def property_count_breakdown(self) -> None:
        """
        Display property counts
        """
        # Generate table headings and set table size
        col_headings = [
            "Return Period (years)", "Properties at risk pre-intervention", "Propeties at risk post-intervention"]
        row_headings = const.initial_aeps
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Populate table
        for i in range(6):
            # Return period
            rp_item = QTableWidgetItem(str(const.initial_return_periods[i]))
            self.table.setItem(i, 0, rp_item)

            # Pre-intervention, formatting included
            pre_item = QTableWidgetItem(
                "{:,.2f}".format(self.db.props_at_risk[i]))
            self.table.setItem(i, 1, pre_item)

            # Post-intervention, formatting included
            post_item = QTableWidgetItem(
                "{:,.2f}".format(self.db.props_at_risk_after[i]))
            self.table.setItem(i, 2, post_item)

    def existing_damages_breakdown(self) -> None:
        """
        Display pre-intervention damages and property counts
        """
        # Generate table headings and set table size
        col_headings = ["Number of Properties at risk",
                        "Lower Annual Damage (£)", "Upper Annual Damage (£)"]
        row_headings = const.initial_aeps + [None, None, None]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        dataset = self.db.get_pre_existing_datapoints()
        for row in range(len(dataset)):
            for col in range(len(dataset[0])):

                # Format numerical entries
                try:
                    item = QTableWidgetItem(
                        "{:,.2f}".format(dataset[row][col]))
                    self.table.setItem(row, col, item)

                except (ValueError, TypeError):
                    item = QTableWidgetItem(dataset[row][col])
                    self.table.setItem(row, col, item)


class ExportResults(QDialog):
    def __init__(self, parent: InitialAppraisal) -> None:
        super().__init__(parent)
        self.parent = parent

        # Display fields
        export_options = [
            "Property Counts",
            "Existing Damages"
        ]
        self.export_btns = [QCheckBox(option) for option in export_options]
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

        # Datapoints groupbox
        datapoints_lyt = QVBoxLayout()
        datapoints_lyt.setSpacing(10)
        for btn in self.export_btns:
            datapoints_lyt.addLayout(utils.centered_hbox(btn))
        datapoints_group = QGroupBox("Datapoints")
        datapoints_group.setLayout(datapoints_lyt)

        # File formats groupbox
        file_format_lyt = QHBoxLayout()
        for btn in self.file_btns:
            file_format_lyt.addLayout(utils.centered_hbox(btn))
        file_format_group = QGroupBox("File Formats")
        file_format_group.setLayout(file_format_lyt)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.check_entries)

        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(25)
        main_lyt.addWidget(text)
        main_lyt.addWidget(datapoints_group)
        main_lyt.addWidget(file_format_group)
        main_lyt.addLayout(utils.centered_hbox(export_btn))
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
## MULTITHREADING ##
####################
"""


class JSONWriteWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, appraisal: InitialAppraisal, fname: str) -> None:
        super().__init__()
        self.appraisal = appraisal
        self.fname = fname

    def run(self) -> None:
        """
        Long-running JSON-writing task
        """
        try:
            with open(f"{self.fname}.trit", "w") as f:
                json.dump(self.appraisal.db.__dict__, f)

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

    def __init__(self, appraisal: InitialAppraisal, fname: str) -> None:
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
