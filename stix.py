"""
Main 

Angus Toms 
22 06 2021
"""
from PyQt5.QtWidgets import (
    QAction, QApplication, QMainWindow, QMenu, QMenuBar, QMessageBox, QStackedWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Page imports
from help_page import HelpPage
from home_page import HomePage
from selection_page import SelectionPage


class Stix(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.stack = QStackedWidget()
        # Menu bar action fields
        self.save_action = QAction("Save Appraisal", self)
        self.export_action = QAction("Export Appraisal", self)

        # Instantiate pages
        self.home = HomePage(self)
        self.selection = SelectionPage(self)

        # Add pages
        # Temporary widgets added in place of appraisal widgets
        self.add_page(self.home, 0)
        self.add_page(self.selection, 1)
        self.add_page(QWidget(), 2)
        self.add_page(QWidget(), 3)
        self.add_page(QWidget(), 4)

        self.select_page(0)

        self.initUI()
        self.init_menu_bar()

    def initUI(self) -> None:
        """ Initialise UI 
        """
        self.setCentralWidget(self.stack)

    def init_menu_bar(self) -> None:
        """ Initialise menu bar
        """
        bar = QMenuBar(self)

        # File menu
        file_menu = QMenu("File", self)

        new_initial = QAction("Initial Appraisal", self)
        new_overview = QAction("Overview Appraisal", self)
        new_detailed = QAction("Detailed Appraisal", self)
        new_initial.setShortcut("Ctrl+1")
        new_overview.setShortcut("Ctrl+2")
        new_detailed.setShortcut("Ctrl+3")
        new_action = QMenu("New", self)
        new_action.addAction(new_initial)
        new_action.addAction(new_overview)
        new_action.addAction(new_detailed)
        new_action.triggered.connect(self.new_appraisal_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_appraisal_action)

        self.save_action.setShortcut("Ctrl+S")

        self.export_action.setShortcut("Ctrl+E")

        file_menu.addMenu(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.export_action)

        # Help menu
        help_menu = QMenu("Help", self)

        help_action = QAction("Stix Help", self)
        help_action.setShortcut("Shift+Ctrl+H")
        help_menu.addAction(help_action)
        help_menu.triggered.connect(self.help_action)

        # Add menus to bar
        bar.addMenu(file_menu)
        bar.addMenu(help_menu)

    def add_page(self, widget: QWidget, index: int) -> None:
        """ Add QWidget to stack at specified indec

        Args:
            widget (QWidget): Widget to add
            index (int): Index for widget to be added at
        """
        # Remove widget currently in arg index
        current = self.stack.widget(index)
        self.stack.removeWidget(current)
        if current is not None:
            current.deleteLater()

        # Add new widget to stack
        self.stack.insertWidget(index, widget)

    def select_page(self, index: int) -> None:
        """ Select page in stack

        Args:
            index (int): Index of page to be selected
        """
        self.stack.setCurrentIndex(index)

        # Update window title
        page_titles = {
            0: "Stix v2.0.1 - Home",
            1: "Stix v2.0.1 - Appraisal Selection",
            2: "Stix v2.0.1 - Initial Appraisal",
            3: "Stix v2.0.1 - Overview Appraisal",
            4: "Stix v2.0.1 - Detailed Appraisal"
        }
        self.setWindowTitle(page_titles[index])

        # Enable/Disable MenuBar actions
        if index < 2:
            self.save_action.setDisabled(True)
            self.export_action.setDisabled(True)

        else:
            self.save_action.setEnabled(True)
            self.export_action.setEnabled(True)

    def new_appraisal_action(self, appraisal_level: QAction) -> None:
        """ Sart new appraisal

        Args:
            appraisal_level (QAction): Level of appraisal selected
        """
        # Ask for confirmation if appraisal is already in process
        if self.stack.currentIndex() > 2:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("All unsaved results will be lost")
            msgbox.setInformativeText("Do you want to proceed?")
            msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msgbox.setEscapeButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.Yes)
            retval = msgbox.exec_()

            if retval == QMessageBox.No:
                return

        # Start appraisals
        if appraisal_level.text() == "Initial Appraisal":
            # Initial
            self.selection.start_inital()

        elif appraisal_level.text() == "Overview Appraisal":
            # Overview
            self.selection.start_overview()

        else:
            # Detailed
            self.selection.start_detailed()

    def open_appraisal_action(self) -> None:
        """ Open appraisal from menu bar action
        """
        # Ask for confirmation if appraisal is already in process
        if self.stack.currentIndex() > 2:
            msgbox = QMessageBox(self)
            msgbox.setWindowModality(Qt.WindowModal)
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("All unsaved results will be lost")
            msgbox.setInformativeText("Do you want to proceed?")
            msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msgbox.setEscapeButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.Yes)
            retval = msgbox.exec_()

            if retval == QMessageBox.No:
                return

        # Move to home page
        self.select_page(0)

        self.home.load_appraisal()

    def help_action(self) -> None:
        """ Start help dialog from MenuBar action
        """
        popup = HelpPage()
        popup.exec_()


def main() -> None:
    import sys
    from utils import get_resource_path
    app = QApplication(sys.argv)
    # Create and set app icon
    app.setWindowIcon(QIcon(get_resource_path("assets/Stix.png")))

    Stix = Stix()
    Stix.showMaximized()

    app.exec_()


if __name__ == "__main__":
    main()