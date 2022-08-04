from help_page_texts import (
    headings, initial_texts, overview_texts, detailed_texts, faq_questions, faq_answers)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QScrollArea,
                             QTabWidget, QVBoxLayout, QWidget)

import utils

# Fonts
title_font = QFont("Arial", 14, weight=QFont.Bold)
body_font = QFont("Arial", 13)


class HelpPage(QDialog):
    """ UI widget for the help page of Stix FAS
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stix v2.0.1 - Help")
        self.initUI()

    def initUI(self) -> None:
        """ Initialise UI
        """
        tabs = QTabWidget()

        # Instantiate tabs
        initial = InitialTab(self)
        overview = OverviewTab(self)
        detailed = DetailedTab(self)
        faq = FAQTab(self)

        # Tab widget setup
        tabs = QTabWidget()
        tabs.addTab(initial, "Initial Appraisal")
        tabs.addTab(overview, "Overview Appraisal")
        tabs.addTab(detailed, "Detailed Appraisal")
        tabs.addTab(faq, "FAQs")

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(tabs)
        main_lyt.addLayout(utils.centered_hbox(close_btn))
        self.setLayout(main_lyt)


"""
#################### 
####### TABS #######
####################
"""


class InitialTab(QWidget):
    """ UI widget for the initial help tab
    """
    def __init__(self, parent: HelpPage) -> None:
        """ 
        Args:
            parent (HelpPage): Help page which tab is placed into
        """
        super().__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self) -> None:
        """ Initialise UI
        """
        # Scroll area setup
        scroll_lyt = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_lyt)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # Create labels
        heading_labels = [QLabel(heading) for heading in headings]
        body_labels = [QLabel(body) for body in initial_texts]

        for i in range(len(heading_labels)):
            # Set fonts
            heading_labels[i].setFont(title_font)
            body_labels[i].setFont(body_font)

            # Set wraps and length
            heading_labels[i].setWordWrap(True)
            body_labels[i].setWordWrap(True)

            # Place labels
            scroll_lyt.addWidget(heading_labels[i])
            scroll_lyt.addWidget(body_labels[i])

            scroll_lyt.addSpacing(25)

        scroll_lyt.addStretch()
        main_lyt = QVBoxLayout()
        main_lyt.addWidget(scroll)
        self.setLayout(main_lyt)


class OverviewTab(QWidget):
    """ UI widget for the overview help tab
    """
    def __init__(self, parent: HelpPage) -> None:
        """
        Args:
            parent (HelpPage): Help page which tab is placed into
        """
        super().__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self) -> None:
        """ Initialise UI
        """
        # Scroll area setup
        scroll_lyt = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_lyt)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # Create labels
        heading_labels = [QLabel(heading) for heading in headings]
        body_labels = [QLabel(body) for body in overview_texts]

        for i in range(len(heading_labels)):
            # Set fonts
            heading_labels[i].setFont(title_font)
            body_labels[i].setFont(body_font)

            # Set wraps
            heading_labels[i].setWordWrap(True)
            body_labels[i].setWordWrap(True)

            # Place labels
            scroll_lyt.addWidget(heading_labels[i])
            scroll_lyt.addWidget(body_labels[i])

            scroll_lyt.addSpacing(25)

        scroll_lyt.addStretch()
        main_lyt = QVBoxLayout()
        main_lyt.addWidget(scroll)
        self.setLayout(main_lyt)


class DetailedTab(QWidget):
    """ UI widget for the detailed help tab
    """
    def __init__(self, parent: HelpPage) -> None:
        """ 
        Args:
            parent (HelpPage): Help page which tab is placed into
        """
        super().__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self) -> None:
        """ Initialise UI
        """
        # Scroll area setup
        scroll_lyt = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_lyt)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # Create labels
        heading_labels = [QLabel(heading) for heading in headings]
        body_labels = [QLabel(body) for body in detailed_texts]

        for i in range(len(heading_labels)):
            # Set fonts
            heading_labels[i].setFont(title_font)
            body_labels[i].setFont(body_font)

            # Set wraps
            heading_labels[i].setWordWrap(True)
            body_labels[i].setWordWrap(True)

            # Place labels
            scroll_lyt.addWidget(heading_labels[i])
            scroll_lyt.addWidget(body_labels[i])

            scroll_lyt.addSpacing(25)

        scroll_lyt.addStretch()
        main_lyt = QVBoxLayout()
        main_lyt.addWidget(scroll)
        self.setLayout(main_lyt)


class FAQTab(QWidget):
    """ UI widget for the FAQ tav
    """
    def __init__(self, parent: HelpPage) -> None:
        """ 
        Args:
            parent (HelpPage): Help page which tab is placed into
        """
        super().__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self) -> None:
        """ Initialise UI
        """
        # Scroll area setup
        scroll_lyt = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_lyt)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # Create labels
        question_labels = [QLabel(question) for question in faq_questions]
        answer_labels = [QLabel(answer) for answer in faq_answers]

        for i in range(len(question_labels)):
            # Set fonts
            question_labels[i].setFont(title_font)
            answer_labels[i].setFont(body_font)

            # Set wraps
            question_labels[i].setWordWrap(True)
            answer_labels[i].setWordWrap(True)

            # Hyperlinking
            answer_labels[i].setOpenExternalLinks(True)

            # Place labels
            scroll_lyt.addWidget(question_labels[i])
            scroll_lyt.addWidget(answer_labels[i])

            scroll_lyt.addSpacing(25)

        scroll_lyt.addStretch()
        main_lyt = QVBoxLayout()
        main_lyt.addWidget(scroll)
        self.setLayout(main_lyt)
