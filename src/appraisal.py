from abc import abstractmethod

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QWidget


from datahandler import DataHandler


class Appraisal(QWidget):
    """ Parent class for Stix FAS appraisals
    """
    def __init__(self, controller, db: DataHandler) -> None:
        """
        Args:
            controller (Stix): QMainWindow that provides access to page switching methods
        """
        super().__init__()
        self.controller = controller 
        self.db = db
        
        # Menubar actions 
        # self.controller.save_action.disconnect()    
        # self.controller.export_action.disconnect()
    
    def return_home(self) -> None:
        """ Close appraisal widget
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
    
    def load_appraisal_error(self, e: Exception) -> None:
        """ Display traceback of error incurred during appraisal load

        Args:
            e (Exception): Error
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("An error occured during the loading of this appraisal")
        msgbox.setDetailedText(f"Traceback: {e}")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setEscapeButton(QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Ok)
        msgbox.exec_()
    
    @abstractmethod 
    def initUI(self) -> None:
        """ Initialise UI
        """
    
    @abstractmethod      
    def load_appraisal(self, fname: str) -> None:
        """ Load appraisal state from saved file

        Args:
            fname (str): Saved .stix file
        """