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

import os
from typing import List

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from body_parser import Attachment
from logger_config import logger
from utils import format_bytes

# Map file extensions (lowercase, without dot) to resource icon aliases.
# Extensions not listed here will fall back to document_green.png.
_EXTENSION_ICON_MAP = {
    "eml": ":/icons/file_extension_eml.png",
    "gif": ":/icons/file_extension_gif.png",
    "htm": ":/icons/file_extension_htm.png",
    "html": ":/icons/file_extension_html.png",
    "jpeg": ":/icons/file_extension_jpeg.png",
    "jpg": ":/icons/file_extension_jpg.png",
    "mp4": ":/icons/file_extension_mp4.png",
    "pdf": ":/icons/file_extension_pdf.png",
    "txt": ":/icons/file_extension_txt.png",
    "wav": ":/icons/file_extension_wav.png",
}

_DEFAULT_ICON = ":/icons/document_green.png"


def _icon_for_filename(filename: str) -> QIcon:
    """Return the appropriate QIcon for the given filename based on its extension."""
    ext = os.path.splitext(filename)[1].lstrip(".").lower()
    icon_path = _EXTENSION_ICON_MAP.get(ext, _DEFAULT_ICON)
    return QIcon(icon_path)


class AttachmentListWidget(QWidget):
    """
    A widget that displays a list of email attachments with file-type icons
    and allows the user to save (download) individual attachments.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._attachments: List[Attachment] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header row: count label + Save All button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self._countLabel = QLabel("No attachments")
        header_layout.addWidget(self._countLabel)
        header_layout.addStretch()

        self._saveAllButton = QPushButton("Save All…")
        self._saveAllButton.setEnabled(False)
        self._saveAllButton.clicked.connect(self._save_all)
        header_layout.addWidget(self._saveAllButton)

        layout.addLayout(header_layout)

        # List widget
        self._listWidget = QListWidget()
        self._listWidget.setIconSize(QSize(24, 24))
        self._listWidget.setSpacing(2)
        self._listWidget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._listWidget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._listWidget)

        # Save selected button
        self._saveButton = QPushButton("Save Selected…")
        self._saveButton.setEnabled(False)
        self._saveButton.clicked.connect(self._save_selected)
        layout.addWidget(self._saveButton)

        self._listWidget.currentItemChanged.connect(self._on_selection_changed)

    # ── public API ────────────────────────────────────────────────────────

    def set_attachments(self, attachments: List[Attachment]):
        """Populate the list with the given attachments."""
        self._attachments = attachments
        self._listWidget.clear()

        count = len(attachments)
        self._countLabel.setText(
            f"{count} attachment{'s' if count != 1 else ''}"
            if count
            else "No attachments"
        )
        self._saveAllButton.setEnabled(count > 0)
        self._saveButton.setEnabled(False)

        for idx, att in enumerate(attachments):
            size_str = format_bytes(len(att.payload))
            text = f"{att.filename}  ({size_str})"
            item = QListWidgetItem(_icon_for_filename(att.filename), text)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self._listWidget.addItem(item)

    def clear(self):
        """Remove all items."""
        self._attachments = []
        self._listWidget.clear()
        self._countLabel.setText("No attachments")
        self._saveAllButton.setEnabled(False)
        self._saveButton.setEnabled(False)

    # ── slots ─────────────────────────────────────────────────────────────

    def _on_selection_changed(self, current: QListWidgetItem, _previous):
        self._saveButton.setEnabled(current is not None)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Double-click triggers save for the clicked attachment."""
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and 0 <= idx < len(self._attachments):
            self._save_attachment(self._attachments[idx])

    def _save_selected(self):
        item = self._listWidget.currentItem()
        if item is None:
            return
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and 0 <= idx < len(self._attachments):
            self._save_attachment(self._attachments[idx])

    def _save_all(self):
        if not self._attachments:
            return
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Save All Attachments"
        )
        if not folder:
            return
        saved = 0
        for att in self._attachments:
            try:
                dest = os.path.join(folder, att.filename)
                # Avoid overwriting – append a number if file exists
                dest = self._unique_path(dest)
                with open(dest, "wb") as f:
                    f.write(att.payload)
                saved += 1
            except Exception as e:
                logger.error(
                    f"Failed to save attachment '{att.filename}': {e}", exc_info=True
                )
                QMessageBox.warning(
                    self,
                    "Save Error",
                    f"Could not save '{att.filename}':\n{e}",
                )
        if saved:
            QMessageBox.information(
                self,
                "Attachments Saved",
                f"Saved {saved} attachment{'s' if saved != 1 else ''} to:\n{folder}",
            )

    # ── helpers ───────────────────────────────────────────────────────────

    def _save_attachment(self, attachment: Attachment):
        """Prompt the user to save a single attachment."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Attachment",
            attachment.filename,
            "All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(attachment.payload)
            logger.info(f"Attachment saved: {path}")
        except Exception as e:
            logger.error(f"Failed to save attachment: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save attachment:\n{e}",
            )

    @staticmethod
    def _unique_path(path: str) -> str:
        """Return a path that doesn't already exist by appending (1), (2), etc."""
        if not os.path.exists(path):
            return path
        base, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists(f"{base} ({counter}){ext}"):
            counter += 1
        return f"{base} ({counter}){ext}"
