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
from PySide6.QtGui import QCursor, QFont, QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QSizePolicy,
    QSpacerItem,
)
from constants import APP_NAME
import resources_rc

# Shared text interaction flags for all selectable labels
_SELECTABLE_TEXT_FLAGS = (
    Qt.TextInteractionFlag.TextSelectableByMouse
    | Qt.TextInteractionFlag.TextSelectableByKeyboard
    | Qt.TextInteractionFlag.LinksAccessibleByMouse
    | Qt.TextInteractionFlag.LinksAccessibleByKeyboard
)


class AboutDialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("About")
        Dialog.resize(504, 431)

        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayoutMain = QGridLayout()
        self.gridLayoutMain.setObjectName("gridLayoutMain")

        self._setup_logo_section(Dialog)
        self._setup_links_section(Dialog)
        self._setup_license_section(Dialog)

        self.gridLayout.addLayout(self.gridLayoutMain, 0, 0, 1, 1)

    def _setup_logo_section(self, Dialog):
        self.horizontalLayoutLogo = QHBoxLayout()
        self.horizontalLayoutLogo.setSpacing(0)
        self.horizontalLayoutLogo.setObjectName("horizontalLayoutLogo")
        self.horizontalLayoutLogo.setSizeConstraint(
            QLayout.SizeConstraint.SetDefaultConstraint
        )

        # Logo image
        self.labelLogo = QLabel(Dialog)
        self.labelLogo.setObjectName("labelLogo")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelLogo.sizePolicy().hasHeightForWidth())
        self.labelLogo.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(17)
        self.labelLogo.setFont(font)
        self.labelLogo.setPixmap(QPixmap(":/icons/logo.png"))
        self.labelLogo.setScaledContents(True)
        self.labelLogo.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )
        self.horizontalLayoutLogo.addWidget(self.labelLogo)

        # Spacer between logo and app name
        self.horizontalLayoutLogo.addItem(
            QSpacerItem(10, 2, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        )

        # App name
        self.labelAppName = QLabel(Dialog)
        self.labelAppName.setObjectName("labelAppName")
        self.labelAppName.setText(APP_NAME)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelAppName.sizePolicy().hasHeightForWidth())
        self.labelAppName.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies(["STSong"])
        font.setPointSize(17)
        font.setBold(True)
        self.labelAppName.setFont(font)
        self.labelAppName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelAppName.setIndent(0)
        self.labelAppName.setTextInteractionFlags(_SELECTABLE_TEXT_FLAGS)
        self.horizontalLayoutLogo.addWidget(self.labelAppName)

        # Right spacer
        self.horizontalLayoutLogo.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        self.gridLayoutMain.addLayout(self.horizontalLayoutLogo, 0, 0, 1, 1)

    def _setup_links_section(self, Dialog):
        self.horizontalLayoutLinks = QHBoxLayout()
        self.horizontalLayoutLinks.setObjectName("horizontalLayoutLinks")
        self.horizontalLayoutLinks.setContentsMargins(-1, 4, -1, 4)

        # "GitHub:" label
        self.labelGitHub = QLabel(Dialog)
        self.labelGitHub.setObjectName("labelGitHub")
        self.labelGitHub.setText("GitHub:")
        self.labelGitHub.setTextInteractionFlags(_SELECTABLE_TEXT_FLAGS)
        self.horizontalLayoutLinks.addWidget(self.labelGitHub)

        # GitHub clickable link
        self.labelGitHubLink = QLabel(Dialog)
        self.labelGitHubLink.setObjectName("labelGitHubLink")
        self.labelGitHubLink.setText(
            '<a href="https://github.com/AlstonChan/py-mailbox-viewer">'
            "https://github.com/AlstonChan/py-mailbox-viewer</a>"
        )
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelGitHubLink.sizePolicy().hasHeightForWidth()
        )
        self.labelGitHubLink.setSizePolicy(sizePolicy)
        font = QFont()
        font.setUnderline(True)
        self.labelGitHubLink.setFont(font)
        self.labelGitHubLink.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.labelGitHubLink.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.labelGitHubLink.setOpenExternalLinks(True)
        self.labelGitHubLink.setTextInteractionFlags(_SELECTABLE_TEXT_FLAGS)
        self.horizontalLayoutLinks.addWidget(self.labelGitHubLink)

        self.gridLayoutMain.addLayout(self.horizontalLayoutLinks, 1, 0, 1, 1)

    def _setup_license_section(self, Dialog):
        self.groupBoxLicense = QGroupBox(Dialog)
        self.groupBoxLicense.setObjectName("groupBoxLicense")
        self.groupBoxLicense.setTitle("Apache 2.0 License")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.groupBoxLicense.sizePolicy().hasHeightForWidth()
        )
        self.groupBoxLicense.setSizePolicy(sizePolicy)
        self.groupBoxLicense.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2 = QGridLayout(self.groupBoxLicense)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.labelLicense = QLabel(self.groupBoxLicense)
        self.labelLicense.setObjectName("labelLicense")
        self.labelLicense.setText(
            "   Copyright 2026 CHAN ALSTON\n"
            "\n"
            '   Licensed under the Apache License, Version 2.0 (the "License");\n'
            "   you may not use this file except in compliance with the License.\n"
            "   You may obtain a copy of the License at\n"
            "\n"
            "       http://www.apache.org/licenses/LICENSE-2.0\n"
            "\n"
            "   Unless required by applicable law or agreed to in writing, software\n"
            '   distributed under the License is distributed on an "AS IS" BASIS,\n'
            "   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
            "   See the License for the specific language governing permissions and\n"
            "   limitations under the License."
        )
        sizePolicy.setHeightForWidth(self.labelLicense.sizePolicy().hasHeightForWidth())
        self.labelLicense.setSizePolicy(sizePolicy)
        self.labelLicense.setWordWrap(True)
        self.labelLicense.setTextInteractionFlags(_SELECTABLE_TEXT_FLAGS)

        self.gridLayout_2.addWidget(self.labelLicense, 0, 0, 1, 1)

        self.gridLayoutMain.addWidget(self.groupBoxLicense, 2, 0, 1, 1)
