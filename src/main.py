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
import email.utils
from typing import List

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
)
from PySide6.QtGui import QAction  # Keep QAction, as it's used in _connect_actions
from PySide6.QtCore import Qt, Signal  # Import Signal for custom signals

from ui.main_window import Ui_MainWindow
from ui.selection_bar import Ui_SelectionBarWidget
from logger_config import logger
from mail_message import MailMessage
from body_parser import create_mbox_body_content_provider
from utils import clear_layout, format_bytes, parse_email_date


# Custom QWidget to handle clicks for selection bar
class ClickableSelectionBar(QWidget):
    clicked = Signal(int)  # Signal to emit when clicked, passing its index

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        # This allows the mousePressEvent to be triggered
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Don't take focus

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._connect_actions()

        self.emails: List[MailMessage] = []  # Initialize emails list
        self.statusBar().showMessage("Ready")

    def _clear_and_load_emails_into_selection_bar(
        self, emails: List[MailMessage]
    ) -> None:
        """
        Clears existing selection bars and populates the selection bar area
        with MailMessage objects.
        """
        # Clear existing widgets from the layout
        clear_layout(self.selectionBarLayout)

        # Add new selection bars
        if not emails:
            self.selectionBarLayout.addStretch(1)  # Add stretch even if no emails
            return

        for index, mail_message in enumerate(emails):
            # Use custom ClickableSelectionBar
            selection_bar_container = ClickableSelectionBar(
                index, self.scrollAreaWidgetContents
            )
            selection_bar_ui = Ui_SelectionBarWidget()
            selection_bar_ui.setupUi(selection_bar_container)

            # Populate with MailMessage data
            # Use 'or "N/A"' for optional fields
            sender_display = (
                mail_message.sender or mail_message.from_ or "Unknown Sender"
            )
            subject_display = mail_message.subject or "No Subject"
            date_display = (
                mail_message.date_header.strftime("%Y-%m-%d %H:%M")
                if mail_message.date_header
                else (mail_message.date or "No Date")
            )
            size_display = format_bytes(mail_message.size)

            selection_bar_ui.labelRecipient.setText(sender_display)
            selection_bar_ui.labelSubject.setText(subject_display)
            selection_bar_ui.labelDateTime.setText(date_display)
            selection_bar_ui.labelSize.setText(size_display)

            # Connect click event
            selection_bar_container.clicked.connect(self.show_email_details)

            self.selectionBarLayout.addWidget(selection_bar_container)

        # Add a stretch to push all selection bars to the top
        self.selectionBarLayout.addStretch(1)

    def _connect_actions(self) -> None:
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
            if self.emails:
                logger.info(f"Loaded {len(self.emails)} emails from {file_path}.")
                self.statusBar().showMessage(f"Loaded {len(self.emails)} emails.")
                self._clear_and_load_emails_into_selection_bar(
                    self.emails
                )  # Populate selection bar
            else:
                logger.warning(f"No emails loaded from {file_path}.")
                self.statusBar().showMessage(f"No emails loaded.")

    def load_emails(self, file_path: str) -> List[MailMessage]:
        emails: List[MailMessage] = []
        try:
            # First, attempt to open as an mbox file, as they can be extensionless
            # The mailbox module detects mbox format by content ("From " lines)
            mbox = mailbox.mbox(file_path)
            # If successful, proceed with mbox parsing
            logger.debug(f"Attempting to load {file_path} as MBOX.")
            for key, message in mbox.items():
                headers = {k: v for k, v in message.items()}
                size = len(message.as_bytes())

                subject = message.get("Subject")
                sender = message.get("From")

                recipients: List[str] = []
                for header_name in ["To", "Cc", "Bcc"]:
                    addresses = email.utils.getaddresses(
                        message.get_all(header_name, [])
                    )
                    recipients.extend([addr for name, addr in addresses if addr])

                date_header_str = message.get("Date")
                date_header = (
                    parse_email_date(date_header_str) if date_header_str else None
                )

                mail_msg = MailMessage(
                    headers=headers,
                    size=size,
                    _body_content_provider=create_mbox_body_content_provider(mbox, key),
                    subject=subject,
                    sender=sender,
                    recipients=recipients,
                    date_header=date_header,
                    message_id=message.get("Message-ID"),
                    source_identifier=f"{file_path}:{key}",
                )
                emails.append(mail_msg)
            return emails
        except mailbox.FormatError:
            logger.debug(
                f"File {file_path} is not a valid MBOX file by content. Checking for other formats."
            )
            # If it's not a valid mbox by content, check by extension
            if file_path.endswith(".eml"):
                # TODO: Implement .eml parsing later
                logger.warning(f"EML file parsing not yet implemented for {file_path}.")
                QMessageBox.information(
                    self, "Info", "EML file parsing is not yet implemented."
                )
            else:
                logger.warning(f"Unsupported file type or invalid format: {file_path}")
                QMessageBox.warning(
                    self,
                    "Unsupported File Type",
                    f"The file '{file_path}' is not a recognized mail format (mbox, eml).",
                )
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file '{file_path}': {e}\nCheck logs for details.",
            )
        return []

    # Renamed from show_email
    def show_email_details(self, index: int):
        """
        Displays the details of the selected email.
        """
        if 0 <= index < len(self.emails):
            mail_message = self.emails[index]
            logger.debug(f"Showing details for email: {mail_message.subject}")
            # Placeholder: In a real app, you'd populate a QTextEdit or similar
            # For example: self.email_text_viewer.setHtml(mail_message.html_body or mail_message.plain_body)
            # For now, just logging the body content to show it's working
            # print("\n--- RAW BODY ---")
            # print(mail_message.raw_body)
            # print("\n--- PLAIN BODY ---")
            # print(mail_message.plain_body)
            # print("\n--- HTML BODY ---")
            # print(mail_message.html_body)
        else:
            logger.warning(
                f"Attempted to show email details for invalid index: {index}"
            )

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
