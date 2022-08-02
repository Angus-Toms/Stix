"""
UI widget for overview appraisals performed by Triton FAS

Angus Toms
17 06 2021
"""
import json
import os

from PyQt5.QtCore import (QObject, Qt, pyqtSignal, QThread)
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QComboBox, QDialog,
                             QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton,
                             QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

import utils
import const
from overview_datahandler import OverviewDataHandler

"""
#################### 
######## MAIN ######
####################
"""


class OverviewAppraisal(QWidget):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

        self.db = OverviewDataHandler()

        self.tabs = QTabWidget()
        self.entry_tab = EntryTab(self, self.db)
        self.results_tab = ResultsTab(self, self.db)

        # Connect MenuBar actions
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
        self.tabs.addTab(self.entry_tab, "Entry")
        self.tabs.addTab(self.results_tab, "Results")

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.tabs)
        self.setLayout(main_lyt)

    def return_home(self) -> None:
        """
        Leave overview appraisal widget
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
            self.thread.finished.connect(self.entry_tab.update_event_details)
            self.thread.finished.connect(
                self.entry_tab.display_cumulative_res_counts)
            self.thread.finished.connect(
                self.entry_tab.display_cumulative_non_res_counts)
            self.thread.finished.connect(self.entry_tab.reload_res_table)
            self.thread.finished.connect(self.entry_tab.reload_non_res_table)
            self.thread.finished.connect(self.results_tab.update_table)

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


class EntryTab(QWidget):
    def __init__(self, parent: OverviewAppraisal, db: OverviewDataHandler) -> None:
        super().__init__()
        self.parent = parent
        self.db = db

        # Flood event details display fields
        self.warning_label = QLabel()
        self.scheme_lifetime_label = QLabel()
        self.location_label = QLabel()
        self.sop_label = QLabel()

        # Property display fields
        self.res_table = QTableWidget()
        self.non_res_table = QTableWidget()

        self.update_event_details()
        self.initUI()
        self.remove_res_double_count()
        self.remove_non_res_double_count()

    def initUI(self) -> None:
        """
        UI Setup
        """
        # Flood event details Groupbox
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.scheme_lifetime_label.setAlignment(Qt.AlignCenter)
        self.location_label.setAlignment(Qt.AlignCenter)
        self.sop_label.setAlignment(Qt.AlignCenter)
        edit_btn = QPushButton("Edit Flood Event Details")
        edit_btn.clicked.connect(self.edit_event_details)

        details_lyt = QVBoxLayout()
        details_lyt.addStretch()
        details_lyt.addWidget(self.scheme_lifetime_label)
        details_lyt.addWidget(self.sop_label)
        details_lyt.addWidget(self.warning_label)
        details_lyt.addWidget(self.location_label)
        details_lyt.addLayout(utils.centered_hbox(edit_btn))
        details_lyt.addStretch()
        details_group = QGroupBox("Flood Event Details")
        details_group.setLayout(details_lyt)

        # Residential Groupbox
        res_text = QLabel(
            "Enter the cumulative number of residential properties at risk")
        res_text.setAlignment(Qt.AlignCenter)
        res_col_headers = ["Properties at risk",
                           "Properties at risk\nNo Double-Count"]
        res_row_headers = const.overview_aeps
        res_row_count, res_col_count = len(
            res_row_headers), len(res_col_headers)
        self.res_table.setRowCount(res_row_count)
        self.res_table.setColumnCount(res_col_count)
        self.res_table.setHorizontalHeaderLabels(res_col_headers)
        self.res_table.setVerticalHeaderLabels(res_row_headers)

        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.res_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        res_lyt = QVBoxLayout()
        res_lyt.setSpacing(15)
        res_lyt.addWidget(res_text)
        res_lyt.addWidget(self.res_table)
        res_group = QGroupBox("Residential Properties")
        res_group.setLayout(res_lyt)

        # Non-residential Groupbox
        non_res_text = QLabel(
            "Enter the cumulative floor area of non-residential properties at risk")
        non_res_text.setAlignment(Qt.AlignCenter)
        non_res_col_headers = []
        for mcm in const.overview_non_res_mcm:
            non_res_col_headers.append(mcm)
            non_res_col_headers.append(f"{mcm}\nNo Double-Count")

        non_res_row_headers = const.overview_aeps
        non_res_row_count, non_res_col_count = len(
            non_res_row_headers), len(non_res_col_headers)
        self.non_res_table.setRowCount(non_res_row_count)
        self.non_res_table.setColumnCount(non_res_col_count)
        self.non_res_table.setHorizontalHeaderLabels(non_res_col_headers)
        self.non_res_table.setVerticalHeaderLabels(non_res_row_headers)
        self.non_res_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.non_res_table.resizeColumnsToContents()

        # Signal connections
        self.res_table.itemSelectionChanged.connect(
            self.remove_res_double_count)
        self.non_res_table.itemSelectionChanged.connect(
            self.remove_non_res_double_count)

        # Input validators
        """
        self.res_table.setItemDelegate(utils.IntegerDelegate())
        self.non_res_table.setItemDelegate(utils.IntegerDelegate())
        """

        # Block input on display columns
        self.res_table.setItemDelegateForColumn(
            1, utils.ReadOnlyDelegate(self.res_table))
        for i in range(1, non_res_col_count, 2):
            self.non_res_table.setItemDelegateForColumn(
                i, utils.ReadOnlyDelegate(self.non_res_table))

        non_res_lyt = QVBoxLayout()
        non_res_lyt.addWidget(non_res_text)
        non_res_lyt.addWidget(self.non_res_table)
        non_res_group = QGroupBox("Non-Residential Properties")
        non_res_group.setLayout(non_res_lyt)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QGridLayout()
        main_lyt.setRowStretch(2, 1)
        main_lyt.addWidget(details_group, 0, 0, 1, 1)
        main_lyt.addWidget(res_group, 0, 1, 1, 1)
        main_lyt.addWidget(non_res_group, 1, 0, 1, 2)
        main_lyt.addLayout(utils.centered_hbox(home_btn), 3, 0, 1, 2)
        self.setLayout(main_lyt)

    def edit_event_details(self) -> None:
        """
        Run the EditFloodDetails dialog
        """
        popup = EditFloodDetails(self, self.db)

        if popup.exec_():
            # Save general flood information
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
        self.warning_label.setText("Flood Warning: {}".format(self.db.warning))
        self.scheme_lifetime_label.setText(
            "Scheme Lifetime: {} years".format(self.db.scheme_lifetime))
        self.location_label.setText("Location: {}".format(self.db.location))
        self.sop_label.setText(
            "Standard of Protection: {} years".format(self.db.sop))

    def remove_res_double_count(self) -> None:
        """
        Read cumulative entries from res_table and remove double count
        """
        # Read entries
        for i in range(7):
            try:
                self.db.cumulative_res_counts[i] = int(
                    self.res_table.item(i, 0).text())

            except (AttributeError, ValueError):
                self.db.cumulative_res_counts[i] = 0

        # Remove double count
        self.db.remove_res_double_count()

        # Reload display
        self.reload_res_table()

    def reload_res_table(self) -> None:
        """
        Display res table entries with double count removed
        """
        for i in range(7):

            # Display any input errors
            if self.db.res_counts[i] >= 0:
                item = QTableWidgetItem(str(self.db.res_counts[i]))

            else:
                if i == 0:
                    item = QTableWidgetItem("Entry must be greater than 0")
                else:
                    item = QTableWidgetItem(
                        f"Entry must be greater than {self.db.cumulative_res_counts[i-1]}")

                item.setBackground(Qt.yellow)

            # Place item
            self.res_table.setItem(i, 1, item)

    def remove_non_res_double_count(self) -> None:
        """
        Read cumulative entries from non res table and remove double count
        """
        # Read entries
        # Iterate through entry columns
        for i in range(len(const.non_res_mcm)):
            for j in range(7):
                try:
                    self.db.cumulative_non_res_counts[i][j] = int(
                        self.non_res_table.item(j, 2*i).text())

                except (AttributeError, ValueError):
                    self.db.cumulative_non_res_counts[i][j] = 0

        # Remove double count
        self.db.remove_non_res_double_count()

        # Reload display
        self.reload_non_res_table()

    def reload_non_res_table(self) -> None:
        """
        Display non res table entries with double count removed
        """
        for i in range(len(const.overview_non_res_mcm)):
            for j in range(7):

                # Display any input errors
                if self.db.non_res_counts[i][j] >= 0:
                    item = QTableWidgetItem(
                        str(self.db.non_res_counts[i][j]))

                else:
                    if j == 0:
                        item = QTableWidgetItem("Entry must be greater than 0")
                    else:
                        item = QTableWidgetItem(
                            f"Entry must be greater than {self.db.cumulative_non_res_counts[i][j-1]}")

                    item.setBackground(Qt.yellow)

                # Place item
                self.non_res_table.setItem(j, (i*2)+1, item)

    def display_cumulative_res_counts(self) -> None:
        """
        Display saved values in cumulative column of res table
        Used for reloading tables after appraisal loading
        """
        for i in range(7):
            item = QTableWidgetItem(str(self.db.cumulative_res_counts[i]))
            self.res_table.setItem(i, 0, item)

    def display_cumulative_non_res_counts(self) -> None:
        """
        Display saved values in cumulative columns of non-res table
        Used for reloading tables after appraisal loading
        """
        for i in range(len(const.overview_non_res_mcm)):
            for j in range(7):
                item = QTableWidgetItem(
                    str(self.db.cumulative_non_res_counts[i][j]))
                self.non_res_table.setItem(j, i*2, item)


class ResultsTab(QWidget):
    def __init__(self, parent: OverviewAppraisal, db: OverviewDataHandler) -> None:
        super().__init__()
        self.parent = parent
        self.db = db

        self.save_results_btn = QPushButton("Save Appraisal")

        self.table = QTableWidget()

        self.initUI()
        self.update_table()

    def initUI(self) -> None:
        """
        UI Setup
        """
        # Results Groupbox
        get_results_btn = QPushButton("Generate Results")
        get_results_btn.clicked.connect(self.get_results)
        col_headers = ["Residential Properties\nAt Risk", "Non-Residential Floor Area\nAt Risk (m²)", "Lower\nResidential Damage",
                       "Upper\nResidential Damage", "Lower\nNon-Residential Damage", "Upper\nNon-Residential Damage", "Lower Total Damage", "Upper Total Damage"]
        row_headers = const.overview_aeps + ["Total", None, None, None, None]
        col_count = len(col_headers)
        row_count = len(row_headers)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headers)
        self.table.setVerticalHeaderLabels(row_headers)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set table spans
        self.table.setSpan(7, 2, 1, 4)
        self.table.setSpan(8, 2, 1, 4)
        self.table.setSpan(9, 2, 1, 4)
        self.table.setSpan(10, 2, 1, 4)
        self.table.setSpan(11, 2, 1, 4)
        self.table.setSpan(8, 0, 4, 2)

        results_lyt = QVBoxLayout()
        results_lyt.addWidget(self.table)
        results_lyt.addLayout(utils.centered_hbox(get_results_btn))
        results_group = QGroupBox("Results")
        results_group.setLayout(results_lyt)

        # Advanced Groupbox
        view_breakdown_btn = QPushButton("View Breakdown")
        view_breakdown_btn.clicked.connect(self.view_breakdown)
        export_results_btn = QPushButton("Export Results")
        export_results_btn.clicked.connect(self.export_results)
        self.save_results_btn.clicked.connect(self.save_results)

        advanced_lyt = QHBoxLayout()
        advanced_lyt.addLayout(utils.centered_hbox(view_breakdown_btn))
        advanced_lyt.addLayout(utils.centered_hbox(export_results_btn))
        advanced_lyt.addLayout(utils.centered_hbox(self.save_results_btn))
        advanced_group = QGroupBox("Advanced")
        advanced_group.setLayout(advanced_lyt)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.parent.return_home)

        main_lyt = QVBoxLayout()
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

                # Format numerical entries
                try:
                    item = QTableWidgetItem(
                        "{:,.2f}".format(datapoints[row][col]))
                    self.table.setItem(row, col, item)

                except (ValueError, TypeError):
                    item = QTableWidgetItem(datapoints[row][col])
                    self.table.setItem(row, col, item)

    def get_results(self) -> None:
        """
        Generate results for currently uploaded flood information
        """
        # Update results fields
        self.db.get_results()

        # Update displays
        self.update_table()

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
            fname = popup.path
            export_options = [btn.isChecked() for btn in popup.export_btns]
            file_formats = [btn.isChecked() for btn in popup.file_btns]

            # Write files
            self.db.export_results(fname, export_options, file_formats)
            utils.write_method_caveats(
                "overview", os.path.join(fname, "Notes"))

    def save_results(self) -> None:
        """
        Save appraisal to .trit file
        """
        fname = utils.get_save_fname(self)

        if fname:
            # Only run if file is selected

            # Instantiate thread and worker
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
##### DIALOGS ######
####################
"""


class EditFloodDetails(QDialog):
    def __init__(self, parent: EntryTab, db: OverviewDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Entry fields
        self.warning_entry = QComboBox()
        self.scheme_lifetime_entry = QSpinBox()
        self.location_entry = QComboBox()
        self.sop_entry = QSpinBox()

        self.setWindowModality(Qt.WindowModal)
        self.initUI()
        self.update_fields()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel("Edit General Flood Information below")
        text.setAlignment(Qt.AlignCenter)

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
        self.warning_entry.setCurrentText(self.db.warning)
        self.scheme_lifetime_entry.setValue(self.db.scheme_lifetime)
        self.location_entry.setCurrentText(self.db.location)
        self.sop_entry.setValue(self.db.sop)


class ResultsBreakdown(QDialog):
    def __init__(self, parent: ResultsTab, db: OverviewDataHandler) -> None:
        super().__init__(parent)
        self.parent = parent
        self.db = db

        # Display fields
        self.table = QTableWidget()

        self.setWindowModality(Qt.WindowModal)
        self.setBaseSize(self.parent.parent.frameGeometry().size())

        self.initUI()

    def initUI(self) -> None:
        """
        UI Setup
        """
        text = QLabel(
            "Here you can view a more advanced breakdown of appraisal results")
        text.setAlignment(Qt.AlignCenter)

        # Breakdown btns
        pre_intervention_res_btn = QPushButton(
            "Pre-intervention Residential Damages"
        )
        post_intervention_res_btn = QPushButton(
            "Post-intervention Residential Damages"
        )
        pre_intervention_non_res_btn = QPushButton(
            "Pre-intervention Non-Residential Damages"
        )
        post_intervention_non_res_btn = QPushButton(
            "Post-intervention Non-Residential Damages"
        )
        pre_intervention_counts_btn = QPushButton(
            "Pre-intervention Property Counts"
        )
        post_intervention_counts_btn = QPushButton(
            "Post-intervention Property Counts"
        )

        # Connections
        pre_intervention_res_btn.clicked.connect(
            self.pre_intervention_res_breakdown
        )
        post_intervention_res_btn.clicked.connect(
            self.post_intervention_res_breakdown
        )
        pre_intervention_non_res_btn.clicked.connect(
            self.pre_intervention_non_res_breakdown
        )
        post_intervention_non_res_btn.clicked.connect(
            self.post_intervention_non_res_breakdown
        )
        pre_intervention_counts_btn.clicked.connect(
            self.pre_intervention_property_counts
        )
        post_intervention_counts_btn.clicked.connect(
            self.post_intervention_property_counts
        )

        btn_lyt_1 = QHBoxLayout()
        btn_lyt_1.addWidget(pre_intervention_res_btn)
        btn_lyt_1.addWidget(post_intervention_res_btn)
        btn_lyt_1.addWidget(pre_intervention_non_res_btn)
        btn_lyt_1.addWidget(post_intervention_non_res_btn)
        btn_lyt_2 = QHBoxLayout()
        btn_lyt_2.addWidget(pre_intervention_counts_btn)
        btn_lyt_2.addWidget(post_intervention_counts_btn)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_1))
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt_2))
        main_lyt.addWidget(self.table)
        main_lyt.addLayout(utils.centered_hbox(close_btn))
        self.setLayout(main_lyt)

    def pre_intervention_res_breakdown(self) -> None:
        """
        Display pre-intervention damages to residential properties
        """
        col_headings = ["Lower Annual Damage (£)", "Upper Annual Damage (£)"]
        row_headings = const.overview_aeps + \
            ["Total Average Annual Damages (£)", "Max Lifetime Damage (£)"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        dataset = [[self.db.lower_res_damages[i],
                    self.db.upper_res_damages[i]] for i in range(7)]
        dataset += [[self.db.lower_annual_res_damage, self.db.upper_annual_res_damage],
                    [self.db.lower_lifetime_res_damage, self.db.upper_lifetime_res_damage]]

        # Populate table
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):

                # Format items
                item = QTableWidgetItem("{:,.2f}".format(dataset[i][j]))
                self.table.setItem(i, j, item)

        # Stretch columns
        self.table.resizeColumnsToContents()

    def post_intervention_res_breakdown(self) -> None:
        """
        Display post-intervention damages to residential properties
        """
        col_headings = ["Lower Annual Damage (£)", "Upper Annual Damage (£)"]
        row_headings = const.overview_aeps + \
            ["Total Average Annual Damages After (£)",
             "Max Lifetime Damage After (£)", "Lifetime Benefit (£)"]
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        dataset = [
            [self.db.lower_res_damages_after[i], self.db.upper_res_damages_after[i]] for i in range(7)
        ]

        dataset += [
            [self.db.lower_annual_res_damage_after,
             self.db.upper_annual_res_damage_after],
            [self.db.lower_lifetime_res_damage_after,
             self.db.upper_lifetime_res_damage_after],
            [self.db.lower_res_benefit, self.db.upper_res_benefit]]

        # Populate table
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):

                # Format items
                item = QTableWidgetItem("{:,.2f}".format(dataset[i][j]))
                self.table.setItem(i, j, item)

        # Stretch columns
        self.table.resizeColumnsToContents()

    def pre_intervention_non_res_breakdown(self) -> None:
        """
        Display pre-intervention damages to non-residential properties
        """
        col_headings = []
        for mcm in const.overview_non_res_mcm:
            col_headings.append(f"{mcm}\nLower Damage (£)")
            col_headings.append(f"{mcm}\nUpper Damage (£)")
        row_headings = const.overview_aeps

        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Flatten 2d list
        dataset = [i for j in zip(
            self.db.lower_non_res_damages, self.db.upper_non_res_damages) for i in j]

        # Add totals
        dataset.append(self.db.lower_total_non_res_damage +
                       [self.db.lower_annual_non_res_damage, self.db.lower_lifetime_non_res_damage])
        dataset.append(self.db.upper_total_non_res_damage +
                       [self.db.upper_annual_non_res_damage, self.db.upper_lifetime_non_res_damage])

        # Populate table
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):

                # Format entries
                item = QTableWidgetItem("{:,.2f}".format(dataset[i][j]))
                self.table.setItem(j, i, item)

        # Turn of column stretching
        self.table.resizeColumnsToContents()

    def post_intervention_non_res_breakdown(self) -> None:
        """
        Display post-intervention damages to non-residential properties
        """
        col_headings = []
        for mcm in const.overview_non_res_mcm:
            col_headings.append(f"{mcm}\nLower Damage (£)")
            col_headings.append(f"{mcm}\nUpper Damage (£)")
        row_headings = const.overview_aeps

        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        # Combine 2 lists
        dataset = [i for j in zip(
            self.db.lower_non_res_damages_after, self.db.upper_non_res_damages_after) for i in j]

        # Populate table
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):

                # Format entries
                item = QTableWidgetItem("{:,.2f}".format(dataset[i][j]))
                self.table.setItem(j, i, item)

        # Turn off column stretching
        self.table.resizeColumnsToContents()

    def pre_intervention_property_counts(self) -> None:
        """
        Display pre-intervention residential and non-residential property counts 
        """
        col_headings = ["Residential Properties\nat risk"] + \
            [f"{mcm}\nFloor Area at risk (m²)" for mcm in const.overview_non_res_mcm]
        row_headings = const.overview_aeps
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        dataset = [self.db.res_counts] + self.db.non_res_counts

        # Populate table
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):

                # Format entries
                item = QTableWidgetItem("{:,.2f}".format(dataset[i][j]))
                self.table.setItem(j, i, item)

        # Turn off column stretching
        self.table.resizeColumnsToContents()

    def post_intervention_property_counts(self) -> None:
        """
        Display post-intervention residential and non-residential property counts
        """
        col_headings = ["Residential Properties\nat risk"] + \
            [f"{mcm}\nFloor Area at risk (m²)" for mcm in const.overview_non_res_mcm]
        row_headings = const.overview_aeps
        row_count, col_count = len(row_headings), len(col_headings)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(col_headings)
        self.table.setVerticalHeaderLabels(row_headings)

        dataset = [self.db.res_counts_after] + self.db.non_res_counts_after

        # Populate table
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):

                # Format entries
                item = QTableWidgetItem("{:,.2f}".format(dataset[i][j]))
                self.table.setItem(j, i, item)

        # Turn off column stretching
        self.table.resizeColumnsToContents()


class ExportResults(QDialog):
    def __init__(self, parent: OverviewAppraisal) -> None:
        super().__init__(parent)
        self.parent = parent

        # Display fields
        export_options = [
            "Pre-intervention residential",
            "Post-intervention residential",
            "Pre-intervention non-residential",
            "Post-intervention non-residential",
            "Pre-intervention property counts",
            "Post-intervention propety counts"
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
        datapoints_group = QGroupBox("Results Breakdowns")
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
### MULTIHREADING ##
####################
"""


class JSONWriteWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, appraisal: OverviewAppraisal, fname: str) -> None:
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

    def __init__(self, appraisal: OverviewAppraisal, fname: str) -> None:
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
