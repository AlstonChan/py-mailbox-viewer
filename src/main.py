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

from typing import List, Optional
import time
from datetime import datetime, timezone

from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QKeySequence, QShortcut

from recent_file_helper import RecentFileHelper
from sort_setting_helper import SortSettingHelper, SortField, SortOrder
from ui.main_window import Ui_MainWindow
from ui.about import AboutDialog
from logger_config import logger
from mail_message import MailMessage
from email_loader import EmailLoaderWorker


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._connect_actions()

        self.emails: List[MailMessage] = []  # Initialize emails list
        self.active_mail_index: Optional[int] = (
            None  # Track currently active email index
        )
        self._loader_thread: Optional[QThread] = None
        self._loader_worker: Optional[EmailLoaderWorker] = None

        self.statusBar().showMessage("Ready")

        recent_files = RecentFileHelper.get_recent_files()
        self.set_recent_files(recent_files, self.open_file)

        # Connect welcome screen's Load File button to open file dialog
        self.welcomeUi.pushButtonLoad.clicked.connect(self.open_file_dialog)

        # Connect virtual selection list click
        self.virtualSelectionList.itemClicked.connect(self.show_email_details)

        # Show welcome screen on startup
        self.show_welcome_screen()

        # Pre-warm the QWebEngineView so that the first real setHtml() call
        # does not trigger a visible Chromium initialization blink.
        self.webEngineViewHtml.setHtml("")

        # Setup keyboard shortcuts for selection navigation
        self._setup_keyboard_shortcuts()

        # Restore saved sort settings into the UI
        self._restore_sort_settings()

    def _connect_actions(self) -> None:
        self.actionOpen.triggered.connect(self.open_file_dialog)
        self.actionReload.triggered.connect(self.reload_data)
        self.actionExit.triggered.connect(self.close)
        self.actionSearch.triggered.connect(self.search_data)
        self.actionFilter.triggered.connect(self.filter_data)
        self.actionExport_Email.triggered.connect(self.export_email)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionShortcuts.triggered.connect(self.show_shortcuts)
        self.actionToggle_preview_pane.triggered.connect(self.toggle_preview_pane)
        self.actionZoom_in_out.triggered.connect(self.zoom_in_out)
        self.actionShow_headers.triggered.connect(self.show_headers)
        self.actionWrap_text.triggered.connect(self.wrap_text)

        # Sort menu connections
        self.sortFieldGroup.triggered.connect(self._on_sort_field_changed)
        self.sortOrderGroup.triggered.connect(self._on_sort_order_changed)

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
        current = self.active_mail_index
        if current is None:
            return
        new_index = current + delta
        if 0 <= new_index < len(self.emails):
            self.show_email_details(new_index)

    # ---------------- Logic ----------------
    def open_file(self, file_path) -> None:
        self.loaded_file_path = file_path
        if file_path:
            logger.debug(f"Opening file: {file_path}")
            self._start_loading(file_path)

    def _start_loading(self, file_path: str) -> None:
        """Start loading emails in a background thread."""
        # Cancel any existing loading operation
        if self._loader_thread is not None and self._loader_thread.isRunning():
            self._loader_thread.quit()
            self._loader_thread.wait()

        self._set_loading_state(True)
        self.statusBar().showMessage(f"Loading mail file: {file_path}...")

        self._loader_thread = QThread()
        self._loader_worker = EmailLoaderWorker(file_path)
        self._loader_worker.moveToThread(self._loader_thread)

        self._loader_thread.started.connect(self._loader_worker.run)
        self._loader_worker.finished.connect(self._on_emails_loaded)
        self._loader_worker.error.connect(self._on_load_error)
        self._loader_worker.finished.connect(self._loader_thread.quit)
        self._loader_worker.error.connect(self._loader_thread.quit)
        self._loader_thread.finished.connect(self._cleanup_loader)

        self._loader_thread.start()

    def _on_emails_loaded(self, emails: List[MailMessage], file_path: str) -> None:
        """Handle successfully loaded emails (called on the main thread)."""
        self.emails = emails
        self._set_loading_state(False)
        if self.emails:
            logger.info(f"Loaded {len(self.emails)} emails from {file_path}.")
            self.statusBar().showMessage(f"Loaded {len(self.emails)} emails.")
            self._sort_emails()
            self.virtualSelectionList.set_emails(self.emails)
            self._user_moved_header_splitter = False
            self.show_email_details(0)
            self.show_email_detail_view()
            RecentFileHelper.add_recent_file(file_path)
            self.set_recent_files(RecentFileHelper.get_recent_files(), self.open_file)
        else:
            logger.warning(f"No emails loaded from {file_path}.")
            self.statusBar().showMessage("No emails loaded.")

    def _on_load_error(self, error_type: str, message: str) -> None:
        """Handle loading errors (called on the main thread)."""
        self._set_loading_state(False)
        self.statusBar().showMessage("Failed to load mail file.")
        if error_type == "info":
            logger.warning(message)
            QMessageBox.information(self, "Info", message)
        elif error_type == "unsupported":
            logger.warning(message)
            QMessageBox.warning(self, "Unsupported File Type", message)
        else:
            logger.error(message)
            QMessageBox.critical(self, "Error", message)

    def _cleanup_loader(self) -> None:
        """Clean up the loader thread and worker after completion."""
        if self._loader_worker is not None:
            self._loader_worker.deleteLater()
            self._loader_worker = None
        if self._loader_thread is not None:
            self._loader_thread.deleteLater()
            self._loader_thread = None

    def _set_loading_state(self, loading: bool) -> None:
        """Enable or disable UI elements during loading."""
        self.actionOpen.setEnabled(not loading)
        self.actionReload.setEnabled(not loading)
        self.actionRecent_Files.setEnabled(not loading)
        self.welcomeUi.pushButtonLoad.setEnabled(not loading)

    def open_file_dialog(self) -> Optional[str]:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Mailbox File",
            "",
            "All Files (*);;Mailbox Files (*.mbox *.msf *.eml)",
        )
        return self.open_file(file_path) if file_path else None

    def show_email_details(self, index: int):
        """
        Displays the details of the selected email in the respective QTextEdit widgets.
        """
        if 0 <= index < len(self.emails):
            mail_message = self.emails[index]
            self.active_mail_index = index

            # Update the virtual selection list highlight and scroll
            self.virtualSelectionList.set_active_index(index)
            self.virtualSelectionList.scroll_to_index(index)

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

            # Populate Attachments tab
            attachments = mail_message.attachments
            if attachments:
                self.tabMailBody.setTabVisible(3, True)
                self.attachmentListWidget.set_attachments(attachments)
            else:
                self.attachmentListWidget.clear()
                self.tabMailBody.setTabVisible(3, False)

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
            self.attachmentListWidget.clear()
            self.tabMailBody.setTabVisible(0, True)  # HTML tab
            self.tabMailBody.setTabVisible(1, True)  # Plain Text tab
            self.tabMailBody.setTabVisible(2, True)  # Raw MIME tab
            self.tabMailBody.setTabVisible(3, True)  # Attachments tab

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

    def _restore_sort_settings(self) -> None:
        """Restore saved sort field and order into the UI menu actions."""
        sort_field = SortSettingHelper.get_sort_field()
        sort_order = SortSettingHelper.get_sort_order()

        field_action_map = {
            SortField.DATE: self.actionSortByDate,
            SortField.SIZE: self.actionSortBySize,
            SortField.TO: self.actionSortByTo,
            SortField.FROM: self.actionSortByFrom,
            SortField.SUBJECT: self.actionSortBySubject,
        }
        action = field_action_map.get(sort_field)
        if action:
            action.setChecked(True)

        if sort_order == SortOrder.ASCENDING:
            self.actionSortAscending.setChecked(True)
        else:
            self.actionSortDescending.setChecked(True)

        logger.debug(
            f"Restored sort settings: field={sort_field.value}, order={sort_order.value}"
        )

    def _on_sort_field_changed(self, action) -> None:
        """Persist the selected sort field when the user changes it."""
        action_field_map = {
            self.actionSortByDate: SortField.DATE,
            self.actionSortBySize: SortField.SIZE,
            self.actionSortByTo: SortField.TO,
            self.actionSortByFrom: SortField.FROM,
            self.actionSortBySubject: SortField.SUBJECT,
        }
        field = action_field_map.get(action)
        if field:
            SortSettingHelper.set_sort_field(field)
            self._apply_sort()

    def _on_sort_order_changed(self, action) -> None:
        """Persist the selected sort order when the user changes it."""
        if action == self.actionSortAscending:
            SortSettingHelper.set_sort_order(SortOrder.ASCENDING)
        elif action == self.actionSortDescending:
            SortSettingHelper.set_sort_order(SortOrder.DESCENDING)
        self._apply_sort()

    def _apply_sort(self) -> None:
        """Sort the current emails and refresh the selection bar, preserving the active email."""
        if not self.emails:
            return

        # Remember the currently viewed email object before re-sorting
        active_mail = (
            self.emails[self.active_mail_index]
            if self.active_mail_index is not None
            and 0 <= self.active_mail_index < len(self.emails)
            else None
        )

        self._sort_emails()
        self.virtualSelectionList.set_emails(self.emails)

        # Restore selection to the same email after re-sorting
        if active_mail is not None:
            try:
                new_index = self.emails.index(active_mail)
            except ValueError:
                new_index = 0
            self.show_email_details(new_index)
        else:
            self.show_email_details(0)

    def _sort_emails(self) -> None:
        """Sort self.emails in-place based on the current sort field and order settings."""
        sort_field = SortSettingHelper.get_sort_field()
        sort_order = SortSettingHelper.get_sort_order()
        reverse = sort_order == SortOrder.DESCENDING

        _DATE_MIN = datetime.min.replace(tzinfo=timezone.utc)

        key_funcs = {
            SortField.DATE: lambda m: m.date_header or _DATE_MIN,
            SortField.SIZE: lambda m: m.size or 0,
            SortField.TO: lambda m: (m.to or "").lower(),
            SortField.FROM: lambda m: (m.from_ or "").lower(),
            SortField.SUBJECT: lambda m: (m.subject or "").lower(),
        }
        key_func = key_funcs.get(sort_field, key_funcs[SortField.DATE])

        self.emails.sort(key=key_func, reverse=reverse)
        logger.debug(
            f"Sorted {len(self.emails)} emails by {sort_field.value} ({sort_order.value})"
        )

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
        dialog = QDialog(self)
        dialog.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowSystemMenuHint
        )
        dialog.setFixedSize(504, 431)
        about_ui = AboutDialog()
        about_ui.setupUi(dialog)
        dialog.exec()

    def show_shortcuts(self):
        logger.debug("Show shortcuts action triggered")

    def toggle_preview_pane(self):
        logger.debug("Toggle preview pane action triggered")

    def zoom_in_out(self):
        logger.debug("Zoom in/out action triggered")

    def show_headers(self):
        logger.debug("Show headers action triggered")

    def wrap_text(self):
        logger.debug("Wrap text action triggered")
