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

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)
from mail_message import MailMessage
from utils import format_bytes
from ui.common.ellipsis_label import EllipsisLabel
from logger_config import logger


class SelectionBarWidget(QWidget):
    """
    A custom QWidget that acts as a clickable selection bar for an email.
    It displays summary information and changes appearance on hover and selection.
    """

    clicked = Signal(int)  # Emits the index of this selection bar when clicked

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self._is_hovered = False  # Internal state for hover effect
        self._is_active = False  # Internal state for active/selected email

        # Track click gesture to avoid emitting on drags / text selection
        self._press_pos = None
        self._pressed = False

        self._setup_ui()
        self._apply_default_style()  # Apply default style initially

    # --- Click handling ---
    def _install_click_forwarding(self) -> None:
        """Install an event filter on child widgets that commonly consume mouse events."""
        # frameMain covers most of the area; labels may accept events (e.g., selectable text)
        for w in [
            getattr(self, "frameMain", None),
            getattr(self, "labelRecipient", None),
            getattr(self, "labelSubject", None),
            getattr(self, "labelDateTime", None),
            getattr(self, "labelSize", None),
        ]:
            if w is not None:
                w.installEventFilter(self)

    def eventFilter(self, watched, event):
        et = event.type()
        # Observe mouse events from children but do NOT consume them.
        # This allows selectable labels to receive press/move/release for text selection
        # while we still detect click gestures by tracking press/move/release positions.
        if et in (
            event.Type.MouseButtonPress,
            event.Type.MouseMove,
            event.Type.MouseButtonRelease,
        ):
            try:
                if et == event.Type.MouseButtonPress:
                    if event.button() == Qt.MouseButton.LeftButton:
                        # Map child-local coordinates to parent (self) coordinates
                        pos = watched.mapTo(self, event.position().toPoint())
                        self._pressed = True
                        self._press_pos = pos
                elif et == event.Type.MouseMove:
                    if self._pressed and self._press_pos is not None:
                        pos = watched.mapTo(self, event.position().toPoint())
                        if (pos - self._press_pos).manhattanLength() >= 4:
                            # User moved enough to constitute a drag/selection
                            self._pressed = False
                elif et == event.Type.MouseButtonRelease:
                    if event.button() == Qt.MouseButton.LeftButton and self._pressed:
                        pos = watched.mapTo(self, event.position().toPoint())
                        if self.rect().contains(pos):
                            logger.debug(f"Selection bar clicked: Index {self.index}")
                            self.clicked.emit(self.index)
                    # Reset press state regardless
                    self._pressed = False
                    self._press_pos = None
            except Exception:
                # Be defensive: don't let unexpected event shapes break selection
                self._pressed = False
                self._press_pos = None
            # Do not consume the event here; allow child widget to handle selection
            return False
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._press_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # If user is selecting text or dragging, don't treat it as a click.
        if self._pressed and self._press_pos is not None:
            if (event.position().toPoint() - self._press_pos).manhattanLength() >= 4:
                self._pressed = False
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            # Only emit if release happens inside the widget
            if self.rect().contains(event.position().toPoint()):
                logger.debug(f"Selection bar clicked: Index {self.index}")
                self.clicked.emit(self.index)
        self._pressed = False
        self._press_pos = None
        super().mouseReleaseEvent(event)

    def _setup_ui(self):
        if not self.objectName():
            self.setObjectName("SelectionBarWidget")

        self._setup_base_widget_properties()
        self._setup_main_frame_and_layouts()
        self._setup_labels()
        self._install_click_forwarding()

    def _setup_base_widget_properties(self):
        self.setWindowModality(Qt.WindowModality.NonModal)
        # Allow the selection bar to receive focus so keyboard navigation can set focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.setMouseTracking(
            True
        )  # Enable mouse tracking for hover events on the widget itself
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )  # Allow horizontal expansion, but not forcing
        self.setMinimumWidth(1)  # Allow to shrink very small if needed

    def _setup_main_frame_and_layouts(self):
        # Setup gridLayout first, as frameMain will be added to it
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # Setup frameMain
        self.frameMain = QFrame(self)
        self.frameMain.setObjectName("frameMain")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameMain.sizePolicy().hasHeightForWidth())
        self.frameMain.setSizePolicy(sizePolicy)
        self.frameMain.setAutoFillBackground(False)
        self.frameMain.setFrameShape(QFrame.Shape.Box)
        self.frameMain.setFrameShadow(QFrame.Shadow.Plain)
        self.frameMain.setMouseTracking(True)  # Enable mouse tracking for frameMain

        # Add frameMain to gridLayout
        self.gridLayout.addWidget(self.frameMain, 0, 0, 1, 1)

        # Setup formLayout (parented to frameMain)
        self.formLayout = QFormLayout(self.frameMain)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setVerticalSpacing(3)
        self.formLayout.setContentsMargins(4, 4, 4, 4)

        # Setup hBoxLayoutTop
        self.hBoxLayoutTop = QHBoxLayout()
        self.hBoxLayoutTop.setSpacing(6)
        self.hBoxLayoutTop.setObjectName("hBoxLayoutTop")
        self.hBoxLayoutTop.setSizeConstraint(
            QLayout.SizeConstraint.SetDefaultConstraint
        )
        self.hBoxLayoutTop.setContentsMargins(-1, -1, -1, 0)

        # Setup spacerVertical
        self.spacerVertical = QSpacerItem(
            0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        # Setup hBoxLayoutBottom
        self.hBoxLayoutBottom = QHBoxLayout()
        self.hBoxLayoutBottom.setObjectName("hBoxLayoutBottom")
        self.hBoxLayoutBottom.setSizeConstraint(
            QLayout.SizeConstraint.SetDefaultConstraint
        )

    def _setup_labels(self):
        font = QFont()
        font.setPointSize(8)

        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)

        # Label Recipient
        self.labelRecipient = EllipsisLabel("", self.frameMain)
        self.labelRecipient.setObjectName("labelRecipient")
        sizePolicy1.setHeightForWidth(
            self.labelRecipient.sizePolicy().hasHeightForWidth()
        )
        self.labelRecipient.setSizePolicy(sizePolicy1)
        self.labelRecipient.setFont(font)
        self.labelRecipient.setAutoFillBackground(False)
        self.labelRecipient.setMargin(0)
        self.labelRecipient.setText("Name <email>")
        self.labelRecipient.setTextInteractionFlags(
            Qt.TextInteractionFlag.NoTextInteraction
        )
        self.hBoxLayoutTop.addWidget(self.labelRecipient)

        # Label DateTime
        self.labelDateTime = QLabel(self.frameMain)
        self.labelDateTime.setObjectName("labelDateTime")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHeightForWidth(
            self.labelDateTime.sizePolicy().hasHeightForWidth()
        )
        self.labelDateTime.setSizePolicy(sizePolicy)
        self.labelDateTime.setFont(font)
        self.labelDateTime.setText("00:00 PM")
        self.labelDateTime.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )
        self.hBoxLayoutTop.addWidget(self.labelDateTime)

        self.formLayout.setLayout(
            0, QFormLayout.ItemRole.SpanningRole, self.hBoxLayoutTop
        )
        self.formLayout.setItem(
            1, QFormLayout.ItemRole.SpanningRole, self.spacerVertical
        )

        # Label Subject
        self.labelSubject = EllipsisLabel("", self.frameMain)
        self.labelSubject.setObjectName("labelSubject")
        sizePolicy1.setHeightForWidth(
            self.labelSubject.sizePolicy().hasHeightForWidth()
        )
        self.labelSubject.setSizePolicy(sizePolicy1)
        self.labelSubject.setFont(font)
        self.labelSubject.setAutoFillBackground(False)
        self.labelSubject.setMargin(0)

        self.hBoxLayoutBottom.addWidget(self.labelSubject)

        self.labelSubject.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        # Do not allow text selection on subject label either
        self.labelSubject.setTextInteractionFlags(
            Qt.TextInteractionFlag.NoTextInteraction
        )
        self.labelSubject.setStyleSheet("padding-right: 6px;")

        # Label Size
        self.labelSize = QLabel(self.frameMain)
        self.labelSize.setObjectName("labelSize")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHeightForWidth(self.labelSize.sizePolicy().hasHeightForWidth())
        self.labelSize.setSizePolicy(sizePolicy)
        self.labelSize.setFont(font)
        self.labelSize.setText("7KB")
        self.hBoxLayoutBottom.addWidget(self.labelSize)

        self.formLayout.setLayout(
            2, QFormLayout.ItemRole.SpanningRole, self.hBoxLayoutBottom
        )

    def _apply_default_style(self):
        self.frameMain.setStyleSheet(
            """
            QFrame#frameMain {
                border: 2px solid palette(mid);
                border-radius: 4px;
                background-color: palette(mid);
                color: palette(mid-text);
            }
            """
        )

    def _apply_hover_style(self):
        # Hover style for frameMain
        self.frameMain.setStyleSheet(
            """
                QFrame#frameMain {
                    border: 2px solid palette(highlight);
                    border-radius: 4px;
                    background-color: palette(alternate-base);
                    color: palette(window-text);
                }
            """
        )

    def _apply_active_style(self):
        # Active style for frameMain
        self.frameMain.setStyleSheet(
            """
                QFrame#frameMain {
                    border: 2px solid palette(highlight);
                    border-radius: 4px;
                    background-color: palette(highlight);
                    color: palette(window-text);
                }
            """
        )

    def set_active(self, active: bool) -> None:
        """
        Sets the active state of the selection bar.
        When active, it uses the active style; otherwise, it determines style based on hover state.
        """
        self._is_active = active
        if active:
            self._apply_active_style()
        else:
            # If no longer active, re-apply hover or default based on current mouse position
            if self._is_hovered:
                self._apply_hover_style()
            else:
                self._apply_default_style()

    def enterEvent(self, event):
        """Event handler for mouse entering the widget area."""
        self._is_hovered = True
        if not self._is_active:  # Only apply hover if not active
            self._apply_hover_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Event handler for mouse leaving the widget area."""
        self._is_hovered = False
        if not self._is_active:  # Only apply default if not active
            self._apply_default_style()
        super().leaveEvent(event)

    def set_email_data(self, mail_message: MailMessage) -> None:
        """
        Populates the selection bar labels with data from a MailMessage object.
        """
        sender_display = mail_message.sender or mail_message.from_ or "Unknown Sender"
        sender_display = sender_display.replace('"', "")

        subject_display = mail_message.subject or "No Subject"
        date_display = (
            mail_message.date_header.strftime("%Y/%m/%d %H:%M")
            if mail_message.date_header
            else (mail_message.date or "No Date")
        )
        size_display = format_bytes(mail_message.size)

        self.labelRecipient.setText(sender_display)
        self.labelSubject.setText(subject_display)
        self.labelDateTime.setText(date_display)
        self.labelSize.setText(size_display)
