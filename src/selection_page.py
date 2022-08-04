from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, QGroupBox)

import utils

# Appraisal imports
from initial_appraisal import InitialAppraisal
from overview_appraisal import OverviewAppraisal
from detailed_appraisal import DetailedAppraisal


# Fonts
title_font = QFont("", weight=QFont.Bold)


class SelectionPage(QWidget):
    """ UI widget for the selection page of Stix FAS  

    """
    def __init__(self, controller) -> None: 
        """ 
        Args:
            controller (Stix): Main QWindow which selection page is placed into
        """
        super().__init__()
        self.controller = controller

        self.initUI()

    def initUI(self) -> None:
        """ Initialise UI
        """
        text = QLabel("Select which appraisal you would like to perform")
        text.setAlignment(Qt.AlignCenter)
        text.setFont(title_font)

        # Initial groupbox
        inital_text = QLabel(
            """Data requriements: Easimap2 Permitting\n\nSuggested Use: Initial Assessment and Pipeline Projects\n\nTime: 2 minutes""")
        inital_text.setAlignment(Qt.AlignCenter)
        initial_btn = QPushButton("Start Initial Appraisal")
        initial_btn.clicked.connect(self.start_inital)

        initial_lyt = QVBoxLayout()
        initial_lyt.addWidget(inital_text)
        initial_lyt.addLayout(utils.centered_hbox(initial_btn))
        initial_group = QGroupBox("Initial Appraisal")
        initial_group.setLayout(initial_lyt)

        # Overview groupbox
        overview_text = QLabel(
            """Data Requirements: NRD,  ArcMap,  and Flood Outlines\n\nSuggested Use: Strategic Outline Case\n\nTime: 10 minutes""")
        overview_text.setAlignment(Qt.AlignCenter)
        overview_btn = QPushButton("Start Overview Appraisal")
        overview_btn.clicked.connect(self.start_overview)

        overview_lyt = QVBoxLayout()
        overview_lyt.addWidget(overview_text)
        overview_lyt.addLayout(utils.centered_hbox(overview_btn))
        overview_group = QGroupBox("Overview Appraisal")
        overview_group.setLayout(overview_lyt)

        # Detailed groupbox
        detailed_text = QLabel(
            """Data Requirements: NRD,  ArcMap,  and Flood Depths\n\nSuggested Use: Outline Business Case\n\nTime: 20 minutes""")
        detailed_text.setAlignment(Qt.AlignCenter)
        detailed_btn = QPushButton("Start Detailed Appraisal")
        detailed_btn.clicked.connect(self.start_detailed)

        detailed_lyt = QVBoxLayout()
        detailed_lyt.addWidget(detailed_text)
        detailed_lyt.addLayout(utils.centered_hbox(detailed_btn))
        detailed_group = QGroupBox("Detailed Appraisal")
        detailed_group.setLayout(detailed_lyt)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.return_home)

        group_lyt = QHBoxLayout()
        group_lyt.addWidget(initial_group)
        group_lyt.addWidget(overview_group)
        group_lyt.addWidget(detailed_group)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(text)
        main_lyt.addLayout(group_lyt)
        main_lyt.addStretch()
        main_lyt.addLayout(utils.centered_hbox(home_btn))
        self.setLayout(main_lyt)

    def start_inital(self) -> None:
        """ Instantiate and display new initial appraisal
        """
        initial = InitialAppraisal(self.controller)

        # Add to stack
        self.controller.add_page(initial, 2)

        # Show
        self.controller.select_page(2)

    def start_overview(self) -> None:
        """ Instantiate and display new overview appraisal
        """
        overview = OverviewAppraisal(self.controller)

        # Add to stack
        self.controller.add_page(overview, 3)

        # Show
        self.controller.select_page(3)

    def start_detailed(self) -> None:
        """ Instantiate and display new detailed appraisal
        """
        detailed = DetailedAppraisal(self.controller)

        # Add to stack
        self.controller.add_page(detailed, 4)

        # Show
        self.controller.select_page(4)

    def return_home(self) -> None:
        """ Leave selection page widget
        """
        self.controller.select_page(0)
