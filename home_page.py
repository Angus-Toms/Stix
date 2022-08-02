"""
UI widget for the home page of Triton FAS

Angus Toms 
23 06 2021
"""
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)

import utils

# Appraisal imports
from detailed_appraisal import DetailedAppraisal
from initial_appraisal import InitialAppraisal
from overview_appraisal import OverviewAppraisal

# Fonts
title_font = QFont("", 16, QFont.Bold)
subtitle_font = QFont("", 14)


class HomePage(QWidget):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

        # Display fields
        self.open_btn = QPushButton("Open Appraisal")

        self.initUI()

    def initUI(self) -> None:
        """
        UI Setup 
        """
        title = QLabel(
            "Welcome to Triton Flood Assessment Systems v2.0.1"
        )
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "Begin or load an appraisal below or view the help page"
        )
        subtitle.setAlignment(Qt.AlignCenter)

        help_btn = QPushButton("Help")
        help_btn.clicked.connect(
            self.controller.help_action
        )
        appraisal_btn = QPushButton("Start Appraisal")
        appraisal_btn.clicked.connect(
            lambda: self.controller.select_page(1)
        )
        self.open_btn.clicked.connect(self.load_appraisal)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        btn_lyt = QHBoxLayout()
        btn_lyt.addWidget(help_btn)
        btn_lyt.addWidget(appraisal_btn)
        btn_lyt.addWidget(self.open_btn)
        btn_lyt.addWidget(close_btn)

        main_lyt = QVBoxLayout()
        main_lyt.addStretch()
        main_lyt.addWidget(title)
        # main_lyt.addSpacing(25)
        main_lyt.addWidget(subtitle)
        main_lyt.addStretch()
        main_lyt.addLayout(utils.centered_hbox_lyt(btn_lyt))
        self.setLayout(main_lyt)

    def close(self) -> None:
        """
        Close window
        """
        msgbox = QMessageBox(self)
        msgbox.setWindowModality(Qt.WindowModal)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setText("Are you sure you want to exit?")
        msgbox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgbox.setEscapeButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.Yes)
        retval = msgbox.exec_()

        if retval == QMessageBox.Yes:
            # Close window
            self.controller.close()

    def load_appraisal(self) -> None:
        """
        Load detailed appraisal from .trit and run
        """
        fname = utils.get_appraisal_fname(self)

        if fname:
            # Only execute if file is selected
            with open(fname, "r") as f:
                field_count = len(json.load(f))

            if field_count == 30:
                # Initial appraisal selected
                appraisal = InitialAppraisal(self.controller)

                # Add to stack and show
                self.controller.add_page(appraisal, 2)
                self.controller.select_page(2)

                # Load information fields
                appraisal.load_appraisal(fname)

            elif field_count == 71:
                # Overview appraisal selected
                appraisal = OverviewAppraisal(self.controller)

                # Add to stack and show
                self.controller.add_page(appraisal, 3)
                self.controller.select_page(3)

                # Load information fields
                appraisal.load_appraisal(fname)

            elif field_count == 162:
                # Detailed appraisal selected
                appraisal = DetailedAppraisal(self.controller)

                # Add to stack and show
                self.controller.add_page(appraisal, 4)
                self.controller.select_page(4)

                # Load information fields
                appraisal.load_appraisal(fname)

            else:
                # JSON file doesn't match any appraisal
                msgbox = QMessageBox(self)
                msgbox.setWindowModality(Qt.WindowModal)
                msgbox.setIcon(QMessageBox.Warning)
                msgbox.setText("Your appriasal couldn't be loaded")
                msgbox.setStandardButtons(QMessageBox.Ok)
                msgbox.setEscapeButton(QMessageBox.Ok)
                msgbox.setDefaultButton(QMessageBox.Ok)
                msgbox.exec_()
