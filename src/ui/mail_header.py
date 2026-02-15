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

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from mail_message import MailMessage
from utils import format_bytes


class MailHeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels: dict[str, QLabel] = (
            {}
        )  # Store references to labels for easy updates
        self._setup_ui()

    def _setup_ui(self):
        if not self.objectName():
            self.setObjectName("MailHeaderWidget")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        # Main layout
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # Central grid layout for left and right sections
        self.gridLayoutMain = QGridLayout()
        self.gridLayoutMain.setObjectName("gridLayoutMain")

        # Left vertical layout for sender/recipient info
        self.verticalLayoutLeft = QVBoxLayout()
        self.verticalLayoutLeft.setSpacing(3)
        self.verticalLayoutLeft.setObjectName("verticalLayoutLeft")

        # Right grid layout for date/size
        self.gridLayoutRight = QGridLayout()
        self.gridLayoutRight.setObjectName("gridLayoutRight")

        # Add layouts to main grid
        self.gridLayoutMain.addLayout(self.verticalLayoutLeft, 0, 0, 1, 1)
        self.gridLayoutMain.addLayout(self.gridLayoutRight, 0, 1, 1, 1)

        # Add central grid to widget's main grid
        self.gridLayout.addLayout(self.gridLayoutMain, 0, 0, 1, 1)

        # Labels and their layouts will be set up in helper methods
        self._setup_labels()

    def _setup_labels(self):
        font_label = QFont()
        font_label.setPointSize(10)
        font_label_bold = QFont()
        font_label_bold.setPointSize(10)
        font_label_bold.setBold(True)

        selectable_label_flags = (
            Qt.TextInteractionFlag.LinksAccessibleByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
            | Qt.TextInteractionFlag.TextSelectableByMouse
        )

        size_policy_preferred = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        size_policy_expanding = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # Helper to create a label and add it to a horizontal layout
        def create_label_row(
            label_key: str,
            label_text: str,
            parent_layout: QHBoxLayout,
            bold_value: bool = False,
        ):
            label = QLabel(self)
            label.setObjectName(f"label{label_key}")
            label.setSizePolicy(size_policy_preferred)
            label.setFont(font_label)
            label.setText(label_text)
            label.setAutoFillBackground(False)
            label.setWordWrap(True)
            label.setMargin(0)
            label.setTextInteractionFlags(selectable_label_flags)
            parent_layout.addWidget(label)
            self.labels[f"label{label_key}"] = label

            value_label = QLabel(self)
            value_label.setObjectName(f"label{label_key}Value")
            value_label.setSizePolicy(size_policy_expanding)
            value_label.setFont(font_label_bold if bold_value else font_label)
            value_label.setText("placeholder")  # Placeholder text
            value_label.setTextInteractionFlags(selectable_label_flags)
            parent_layout.addWidget(value_label)
            self.labels[f"label{label_key}Value"] = value_label

        # From
        self.horizontalLayoutFrom = QHBoxLayout()
        self.horizontalLayoutFrom.setObjectName("horizontalLayoutFrom")
        create_label_row("From", "from:", self.horizontalLayoutFrom, bold_value=True)
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutFrom)

        # Reply-To
        self.horizontalLayoutReplyTo = QHBoxLayout()
        self.horizontalLayoutReplyTo.setObjectName("horizontalLayoutReplyTo")
        create_label_row(
            "ReplyTo", "reply-to:", self.horizontalLayoutReplyTo, bold_value=True
        )
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutReplyTo)

        # To
        self.horizontalLayoutTo = QHBoxLayout()
        self.horizontalLayoutTo.setObjectName("horizontalLayoutTo")
        create_label_row("To", "to:", self.horizontalLayoutTo, bold_value=True)
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutTo)

        # Cc
        self.horizontalLayoutCc = QHBoxLayout()
        self.horizontalLayoutCc.setObjectName("horizontalLayoutCc")
        create_label_row("Cc", "cc:", self.horizontalLayoutCc, bold_value=True)
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutCc)

        # Bcc
        self.horizontalLayoutBcc = QHBoxLayout()
        self.horizontalLayoutBcc.setObjectName("horizontalLayoutBcc")
        create_label_row("Bcc", "bcc:", self.horizontalLayoutBcc, bold_value=True)
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutBcc)

        # Mailed-By
        self.horizontalLayoutMailedBy = QHBoxLayout()
        self.horizontalLayoutMailedBy.setObjectName("horizontalLayoutMailedBy")
        create_label_row(
            "MailedBy", "mailed by:", self.horizontalLayoutMailedBy, bold_value=True
        )
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutMailedBy)

        # Message-Id
        self.horizontalLayoutMessageId = QHBoxLayout()
        self.horizontalLayoutMessageId.setObjectName("horizontalLayoutMessageId")
        create_label_row(
            "MessageId", "message-id:", self.horizontalLayoutMessageId, bold_value=True
        )
        self.verticalLayoutLeft.addLayout(self.horizontalLayoutMessageId)

        self.verticalSpacerContent = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.verticalLayoutLeft.addItem(self.verticalSpacerContent)

        right_view_label_alignment = (
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignTop
        )

        # Date/Time
        self.labelDateTime = QLabel(self)
        self.labelDateTime.setObjectName("labelDateTime")
        self.labelDateTime.setSizePolicy(size_policy_preferred)
        self.labelDateTime.setFont(font_label)
        self.labelDateTime.setAlignment(right_view_label_alignment)
        self.labelDateTime.setTextInteractionFlags(selectable_label_flags)
        self.labelDateTime.setText("00:00 PM")  # Placeholder text
        self.gridLayoutRight.addWidget(self.labelDateTime, 0, 0, 1, 1)

        # Mail Size
        self.labelMailSize = QLabel(self)
        self.labelMailSize.setObjectName("labelMailSize")
        self.labelMailSize.setSizePolicy(size_policy_preferred)
        self.labelMailSize.setFont(font_label)
        self.labelMailSize.setAlignment(right_view_label_alignment)
        self.labelMailSize.setTextInteractionFlags(selectable_label_flags)
        self.labelMailSize.setText("7KB")  # Placeholder text
        self.gridLayoutRight.addWidget(self.labelMailSize, 1, 0, 1, 1)

        self.verticalSpacerSide = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.gridLayoutRight.addItem(self.verticalSpacerSide, 2, 0, 1, 1)

    def set_email_data(self, mail_message: MailMessage) -> None:
        """
        Populates the mail header labels with data from a MailMessage object.
        """
        self.labels["labelFromValue"].setText(mail_message.sender or "N/A")
        self.labels["labelReplyToValue"].setText(mail_message.reply_to or "N/A")
        self.labels["labelToValue"].setText(
            ", ".join(mail_message.formatted_to_full)
            if mail_message.formatted_to_full
            else "N/A"
        )
        self.labels["labelCcValue"].setText(
            ", ".join(mail_message.formatted_cc_full)
            if mail_message.formatted_cc_full
            else "N/A"
        )
        self.labels["labelBccValue"].setText(
            ", ".join(mail_message.formatted_bcc_full)
            if mail_message.formatted_bcc_full
            else "N/A"
        )
        self.labels["labelMailedByValue"].setText(mail_message.mailed_by or "N/A")
        self.labels["labelMessageIdValue"].setText(mail_message.message_id or "N/A")
        self.labelDateTime.setText(
            mail_message.date_header.strftime("%Y/%m/%d %H:%M")
            if mail_message.date_header
            else (mail_message.date or "N/A")
        )
        self.labelMailSize.setText(format_bytes(mail_message.size))
