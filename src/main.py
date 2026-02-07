# Copyright 2026 Chan Alston

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mailbox
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QListWidget,
    QTextEdit,
    QSplitter,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from ui_main_window import Ui_MainWindow
from ui_selection_bar import Ui_SelectionBarWidget
from logger_config import logger


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._setup_ui_elements()
        self._connect_actions()
        self._populate_selection_bar()

        self.emails = []
        self.statusBar().showMessage("Ready")

    def _setup_ui_elements(self):
        # The QListWidget and QTextEdit are no longer needed as selection bars are used.
        pass

    def _populate_selection_bar(self):
        # Create a QVBoxLayout for the scrollAreaWidgetContents to hold selection bars
        self.selectionBarLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.selectionBarLayout.setContentsMargins(0, 0, 0, 0)
        self.selectionBarLayout.setSpacing(5)  # Add some spacing between selection bars

        for i in range(20):
            selection_bar_container = QWidget()
            selection_bar_ui = Ui_SelectionBarWidget()
            selection_bar_ui.setupUi(selection_bar_container)
            self.selectionBarLayout.addWidget(selection_bar_container)

        # Add a stretch to push all selection bars to the top
        self.selectionBarLayout.addStretch(1)

    def _connect_actions(self):
        self.actionOpen.triggered.connect(self.open_file)
        self.actionReload.triggered.connect(self.reload_data)
        self.actionExit.triggered.connect(self.close)
        self.actionSearch.triggered.connect(self.search_data)
        self.actionFilter.triggered.connect(self.filter_data)
        self.actionExport_Email.triggered.connect(self.export_email)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionShortcuts.triggered.connect(self.show_shortcuts)
        self.actionGitHub.triggered.connect(self.show_github)
        self.actionToggle_preview_pane.triggered.connect(self.toggle_preview_pane)
        self.actionZoom_in_out.triggered.connect(self.zoom_in_out)
        self.actionShow_headers.triggered.connect(self.show_headers)
        self.actionWrap_text.triggered.connect(self.wrap_text)

    # ---------------- Logic ----------------
    def open_file(self):
        file_dialog: QFileDialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Open Mailbox File",
            "",
            "Mailbox Files (*.mbox *.msf *.eml);;All Files (*)",
        )
        if file_path:
            logger.debug(f"Opening file: {file_path}")
            self.emails = self.load_emails(file_path)
            logger.info(f"Loaded {len(self.emails)} emails.")

    def load_emails(self, path):
        """
        Temporary fake parser.
        Replace this later with Thunderbird / mbox parsing.
        """
        return []  # Return empty list as per instruction

    def show_email(self, row):
        logger.debug(f"Show email for row {row} - (display logic removed for now)")
        pass  # Display logic removed as per instruction

    def reload_data(self):
        logger.debug("Reload data action triggered")

    def search_data(self):
        logger.debug("Search data action triggered")

    def filter_data(self):
        logger.debug("Filter data action triggered")

    def export_email(self):
        logger.debug("Export email action triggered")

    def show_about(self):
        logger.debug("Show about action triggered")

    def show_shortcuts(self):
        logger.debug("Show shortcuts action triggered")

    def show_github(self):
        logger.debug("Show GitHub action triggered")

    def toggle_preview_pane(self):
        logger.debug("Toggle preview pane action triggered")

    def zoom_in_out(self):
        logger.debug("Zoom in/out action triggered")

    def show_headers(self):
        logger.debug("Show headers action triggered")

    def wrap_text(self):
        logger.debug("Wrap text action triggered")
