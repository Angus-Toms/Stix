import json
import os
from typing import List

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import QObject, pyqtSignal

import utils

from detailed_appraisal_utils import read_table_with_columns


class JSONWriteWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    
    def __init__(self, appraisal, fname: str) -> None:
        super().__init__()
        self.appraisal = appraisal 
        self.fname = fname 
        
    def run(self) -> None:
        """ Write appraisal object to file
        """
        try:
            with open(f"{self.fname}.stix", "w") as f:
                json.dump(self.appraisal.db.__dict__, f, cls=utils.NumpyEncoder)
                
        except Exception as e:
            self.error.emit(e)
            
            # Delete half-written results file
            if os.path.exists(f"{self.fname}.stix"):
                os.remove(f"{self.fname}.six")
                
        # Execution finished 
        self.finished.emit()
        

class JSONLoadWorker(QObject):
    # Signal fields 
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    
    def __init__(self, appraisal, fname: str) -> None:
        super().__init__()
        self.appraisal = appraisal 
        self.fname = fname 
        
    def run(self) -> None:
        """ Load saved appraisal into datahandler object
        """
        try:
            with open(self.fname, "r") as f:
                self.appraisal.db.__dict__ = json.load(f)
                
        except Exception as e:
            self.error.emit(e)
            
        # Execution finished
        self.finished.emit()
            
  
class AsciiUploadWorker(QObject):
    # Signal fields
    finished = pyqtSignal()
    progress = pyqtSignal(float)
    error = pyqtSignal(Exception, str)
    
    def __init__(self, appraisal, fnames: List[str]) -> None :
        super().__init__()
        self.appraisal = appraisal 
        self.fnames = fnames 
        
    def run(self) -> None:
        """ Read details of selected ASCII grids into datahandler
        """   
        ascii_count = len(self.fnames)
        
        try:
            for i in range(ascii_count):
                self.appraisal.db.add_ascii(self.fnames[i])
                # Update UI with upload progress
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
    
    def __init__(self, appraisal, columns: List[int], table: QTableWidget) -> None:
        super().__init__()
        self.appraisal = appraisal 
        self.columns = columns 
        self.table = table 
        
    def run(self) -> None:
        """ Read property details into datahandler
        """
        try:
            props = read_table_with_columns(self.columns, self.table)
            prop_count = len(props)
            for i in range(prop_count):
                self.appraisal.db.add_prop(props[i])
                # Update UI with upload progress
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
    
    def __init__(self, appraisal, columns: List[int], table: QTableWidget) -> None:
        super().__init__()
        self.appraisal = appraisal 
        self.columns = columns 
        self.table = table 
        
    def run(self) -> None:
        """ Read node details into datahandler
        """
        try:
            nodes = read_table_with_columns(self.columns, self.table)
            node_count = len(nodes)
            for i in range(node_count):
                self.appraisal.db.add_node(nodes[i])
                # Update UI with upload progress 
                self.progress.emit(i/node_count)
                
        except Exception as e:
            self.error.emit(e)
            
        # Execution finished 
        self.finished.emit()
            
