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

from collections import defaultdict
import mailbox
import email.utils
from typing import List, Optional
import time

from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from recent_file_helper import RecentFileHelper
from ui.main_window import Ui_MainWindow
from ui.selection_bar import (
    SelectionBarWidget,
)
from logger_config import logger
from mail_message import MailMessage
from body_parser import create_mbox_body_content_provider
from utils import (
    clear_layout,
    parse_email_date,
)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._connect_actions()

        self.emails: List[MailMessage] = []  # Initialize emails list
        self.active_mail_index: Optional[int] = (
            None  # Track currently active email index
        )
        self._current_active_selection_bar: Optional[SelectionBarWidget] = None
        self._selection_bar_widgets: List[SelectionBarWidget] = []

        self.statusBar().showMessage("Ready")

        recent_files = RecentFileHelper.get_recent_files()
        self.set_recent_files(recent_files, self.open_file)

        # Connect welcome screen's Load File button to open file dialog
        self.welcomeUi.pushButtonLoad.clicked.connect(self.open_file_dialog)

        # Show welcome screen on startup
        self.show_welcome_screen()

        # Setup keyboard shortcuts for selection navigation
        self._setup_keyboard_shortcuts()

    def _clear_and_load_emails_into_selection_bar(
        self, emails: List[MailMessage]
    ) -> None:
        """
        Clears existing selection bars and populates the selection bar area
        with MailMessage objects.
        """
        # Clear existing widgets from the layout
        clear_layout(self.selectionBarLayout)  # Using clear_layout from utils
        self._selection_bar_widgets.clear()  # Clear references to old widgets                                                                      │
        self._current_active_selection_bar = None  # Clear active selection

        # Add new selection bars
        if not emails:
            self.selectionBarLayout.addStretch(1)  # Add stretch even if no emails
            return

        for index, mail_message in enumerate(emails):
            selection_bar_widget = SelectionBarWidget(
                index, self.scrollAreaWidgetContents
            )
            selection_bar_widget.set_email_data(mail_message)
            selection_bar_widget.clicked.connect(self.show_email_details)

            self.selectionBarLayout.addWidget(selection_bar_widget)
            self._selection_bar_widgets.append(
                selection_bar_widget
            )  # Store widget reference

        # Add a stretch to push all selection bars to the top
        self.selectionBarLayout.addStretch(1)

    def _connect_actions(self) -> None:
        self.actionOpen.triggered.connect(self.open_file_dialog)
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

    def _setup_keyboard_shortcuts(self):
        """Create application-scoped Up/Down shortcuts to navigate selection bars.

        Using ApplicationShortcut ensures the shortcuts work even when focus is inside
        a child widget that would otherwise consume arrow key events (e.g., scroll areas).
        """
        # Up
        shortcut_up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        shortcut_up.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut_up.activated.connect(lambda: self._move_selection(-1))

        # Down
        shortcut_down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        shortcut_down.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut_down.activated.connect(lambda: self._move_selection(1))

    def _move_selection(self, delta: int):
        """Move selection by delta (-1 for up, +1 for down) and show details.

        Does nothing if there's no active selection or if the new index would be out of bounds.
        """
        current = getattr(self, "active_mail_index", None)
        if current is None:
            return
        new_index = current + delta
        if 0 <= new_index < len(self.emails):
            self.show_email_details(new_index)

            # Ensure the selected widget is visible in the left scroll area
            try:
                if hasattr(self, "scrollAreaLeft") and self._selection_bar_widgets:
                    widget = self._selection_bar_widgets[new_index]
                    # Use the UI method to handle scrolling
                    self.ensure_selection_bar_visible(
                        self._selection_bar_widgets, widget, delta
                    )
                    widget.setFocus()
            except Exception:
                logger.exception(
                    "Failed to ensure selection visible after keyboard navigation"
                )

    # ---------------- Logic ----------------
    def open_file(self, file_path) -> None:
        self.loaded_file_path = file_path  # Save the file path for potential reload
        if file_path:
            logger.debug(f"Opening file: {file_path}")
            self.emails = self.load_emails(file_path)
            if self.emails:
                logger.info(f"Loaded {len(self.emails)} emails from {file_path}.")
                self.statusBar().showMessage(f"Loaded {len(self.emails)} emails.")
                self._clear_and_load_emails_into_selection_bar(self.emails)
                # Switch to email detail view
                self.show_email_detail_view()
                # Auto select the first email if available
                if self.emails:
                    self.show_email_details(0)
                    RecentFileHelper.add_recent_file(file_path)
                    self.set_recent_files(
                        RecentFileHelper.get_recent_files(), self.open_file
                    )
            else:
                logger.warning(f"No emails loaded from {file_path}.")
                self.statusBar().showMessage(f"No emails loaded.")

    def open_file_dialog(self) -> Optional[str]:
        file_dialog: QFileDialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Open Mailbox File",
            "",
            "All Files (*);;Mailbox Files (*.mbox *.msf *.eml)",
        )
        return self.open_file(file_path) if file_path else None

    def load_emails(self, file_path: str) -> List[MailMessage]:
        emails: List[MailMessage] = []
        try:
            # First, attempt to open as an mbox file, as they can be extensionless
            # The mailbox module detects mbox format by content ("From " lines)
            mbox = mailbox.mbox(file_path)
            # If successful, proceed with mbox parsing
            logger.debug(f"Attempting to load {file_path} as MBOX.")
            for (
                key,
                message,
            ) in mbox.items():  # message is not used, so I can pass mbox and key
                headers = defaultdict(list)
                for k, v in message.items():
                    headers[k].append(str(v))
                headers = dict(headers)

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

    def show_email_details(self, index: int):
        """
        Displays the details of the selected email in the respective QTextEdit widgets.
        """
        if 0 <= index < len(self.emails):
            mail_message = self.emails[index]
            self.active_mail_index = index

            if self._current_active_selection_bar is not None:
                self._current_active_selection_bar.set_active(False)

            newly_active_bar = self._selection_bar_widgets[index]
            newly_active_bar.set_active(True)
            self._current_active_selection_bar = newly_active_bar

            # Ensure the newly selected bar is visible in the left scroll area
            try:
                self.ensure_selection_bar_visible(
                    self._selection_bar_widgets, newly_active_bar
                )
                newly_active_bar.setFocus()
            except Exception:
                logger.exception(
                    "Failed to ensure selection visible after show_email_details"
                )

            logger.debug(f"Showing details for email: {mail_message.subject}")
            start_time = time.perf_counter()

            # Populate HTML tab
            if mail_message.html_body:
                self.tabMailBody.setTabVisible(0, True)
                self.webEngineViewHtml.setHtml(mail_message.html_body)
            else:
                self.webEngineViewHtml.setHtml("")
                self.tabMailBody.setTabVisible(0, False)

            # Populate Plain Text tab
            if mail_message.plain_body:
                self.tabMailBody.setTabVisible(1, True)
                self.textEditPlain.setPlainText(mail_message.plain_body)
            else:
                self.textEditPlain.setPlainText("")
                self.tabMailBody.setTabVisible(1, False)

            # Populate Raw MIME tab
            if mail_message.raw_body:
                self.tabMailBody.setTabVisible(2, True)
                self.textEditRaw.setPlainText(mail_message.raw_body)
            else:
                self.textEditRaw.setPlainText("")
                self.tabMailBody.setTabVisible(2, False)

            # Always select the first available tab
            for i in range(self.tabMailBody.count()):
                if self.tabMailBody.isTabVisible(i):
                    self.tabMailBody.setCurrentIndex(i)
                    break

            self.mailHeader.set_email_data(mail_message)

            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.debug(
                f"Email details displayed in {duration:.4f} seconds for email: {mail_message.subject}"
            )
            self.statusBar().showMessage(
                f"Loaded email details in {duration*1000:.2f} ms."
            )

        else:
            logger.warning(
                f"Attempted to show email details for invalid index: {index}"
            )
            # Clear content and ensure all tabs are visible if index is invalid
            self.webEngineViewHtml.setHtml("")
            self.textEditPlain.setPlainText("")
            self.textEditRaw.setPlainText("")
            self.tabMailBody.setTabVisible(0, True)  # HTML tab
            self.tabMailBody.setTabVisible(1, True)  # Plain Text tab
            self.tabMailBody.setTabVisible(2, True)  # Raw MIME tab

    def keyPressEvent(self, event):
        """Handle Up/Down arrow keys to change the selected email.

        - Up: select previous email (index - 1) if not already at top
        - Down: select next email (index + 1) if not already at bottom
        If there is no active selection, keys do nothing.
        """
        try:
            key = event.key()
        except Exception:
            return super().keyPressEvent(event)

        if key == Qt.Key.Key_Up:
            current = getattr(self, "active_mail_index", None)
            if current is not None and current > 0:
                self.show_email_details(current - 1)
                event.accept()
                return
        elif key == Qt.Key.Key_Down:
            current = getattr(self, "active_mail_index", None)
            if current is not None and current < (len(self.emails) - 1):
                self.show_email_details(current + 1)
                event.accept()
                return

        return super().keyPressEvent(event)

    def reload_data(self):
        logger.debug("Reload data action triggered")
        if hasattr(self, "loaded_file_path") and self.loaded_file_path:
            logger.info(f"Reloading data from: {self.loaded_file_path}")
            self.open_file(self.loaded_file_path)
        else:
            logger.warning("No file path to reload. Open a file first.")
            QMessageBox.warning(self, "Warning", "No file loaded to reload from.")

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
