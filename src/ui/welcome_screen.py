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

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QCursor,
    QFont,
    QIcon,
    QPixmap,
)
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class WelcomeFrame(object):
    def setupUi(self, WelcomeFrame):
        if not WelcomeFrame.objectName():
            WelcomeFrame.setObjectName("WelcomeFrame")
        WelcomeFrame.resize(510, 488)
        WelcomeFrame.setAutoFillBackground(False)

        self.gridLayoutParent = QGridLayout(WelcomeFrame)
        self.gridLayoutParent.setObjectName("gridLayoutParent")

        self.gridLayoutMain = QGridLayout()
        self.gridLayoutMain.setObjectName("gridLayoutMain")

        # Vertical spacers to push content to centre
        self.verticalSpacerTop = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.gridLayoutMain.addItem(self.verticalSpacerTop, 0, 0, 1, 1)

        self.verticalSpacerBottom = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.gridLayoutMain.addItem(self.verticalSpacerBottom, 4, 0, 1, 1)

        self._setup_logo_section(WelcomeFrame)
        self._setup_text_section(WelcomeFrame)
        self._setup_cta_section(WelcomeFrame)

        self.gridLayoutMain.setRowMinimumHeight(3, 40)
        self.gridLayoutParent.addLayout(self.gridLayoutMain, 0, 0, 1, 1)

        self.retranslateUi(WelcomeFrame)

        self.pushButtonLoad.setDefault(True)

        QMetaObject.connectSlotsByName(WelcomeFrame)

    def _setup_logo_section(self, WelcomeFrame):
        """Set up the centred logo image at row 1."""
        self.horizontalLayoutLogo = QHBoxLayout()
        self.horizontalLayoutLogo.setSpacing(0)
        self.horizontalLayoutLogo.setObjectName("horizontalLayoutLogo")
        self.horizontalLayoutLogo.setSizeConstraint(
            QLayout.SizeConstraint.SetDefaultConstraint
        )

        self.horizontalSpacerLogoLeft = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayoutLogo.addItem(self.horizontalSpacerLogoLeft)

        self.labelLogo = QLabel(WelcomeFrame)
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

        self.horizontalSpacerLogoRight = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayoutLogo.addItem(self.horizontalSpacerLogoRight)

        self.gridLayoutMain.addLayout(self.horizontalLayoutLogo, 1, 0, 1, 1)

    def _setup_text_section(self, WelcomeFrame):
        """Set up the welcome title and description labels at row 2."""
        font_title = QFont()
        font_title.setPointSize(17)

        font_title_bold = QFont()
        font_title_bold.setFamilies(["STSong"])
        font_title_bold.setPointSize(17)
        font_title_bold.setBold(True)

        font_desc = QFont()
        font_desc.setPointSize(11)

        self.verticalLayoutText = QVBoxLayout()
        self.verticalLayoutText.setObjectName("verticalLayoutText")
        self.verticalLayoutText.setContentsMargins(-1, 10, -1, 10)

        # Title row: "Welcome to" + app name
        self.horizontalLayoutTitle = QHBoxLayout()
        self.horizontalLayoutTitle.setObjectName("horizontalLayoutTitle")

        self.horizontalSpacerTitleLeft = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayoutTitle.addItem(self.horizontalSpacerTitleLeft)

        self.labelWelcomeTo = QLabel(WelcomeFrame)
        self.labelWelcomeTo.setObjectName("labelWelcomeTo")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelWelcomeTo.sizePolicy().hasHeightForWidth()
        )
        self.labelWelcomeTo.setSizePolicy(sizePolicy)
        self.labelWelcomeTo.setFont(font_title)
        self.labelWelcomeTo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayoutTitle.addWidget(self.labelWelcomeTo)

        self.labelAppName = QLabel(WelcomeFrame)
        self.labelAppName.setObjectName("labelAppName")
        sizePolicy.setHeightForWidth(self.labelAppName.sizePolicy().hasHeightForWidth())
        self.labelAppName.setSizePolicy(sizePolicy)
        self.labelAppName.setFont(font_title_bold)
        self.labelAppName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayoutTitle.addWidget(self.labelAppName)

        self.horizontalSpacerTitleRight = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayoutTitle.addItem(self.horizontalSpacerTitleRight)

        self.verticalLayoutText.addLayout(self.horizontalLayoutTitle)

        # Description label
        self.labelDesc = QLabel(WelcomeFrame)
        self.labelDesc.setObjectName("labelDesc")
        self.labelDesc.setFont(font_desc)
        self.labelDesc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayoutText.addWidget(self.labelDesc)

        self.gridLayoutMain.addLayout(self.verticalLayoutText, 2, 0, 1, 1)

    def _setup_cta_section(self, WelcomeFrame):
        """Set up the centred 'Load File' button at row 3."""
        self.horizontalLayoutCTA = QHBoxLayout()
        self.horizontalLayoutCTA.setObjectName("horizontalLayoutCTA")

        self.horizontalSpacerCTALeft = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayoutCTA.addItem(self.horizontalSpacerCTALeft)

        self.pushButtonLoad = QPushButton(WelcomeFrame)
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(76)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(
            self.pushButtonLoad.sizePolicy().hasHeightForWidth()
        )
        self.pushButtonLoad.setSizePolicy(sizePolicy)
        self.pushButtonLoad.setMinimumSize(QSize(0, 0))
        self.pushButtonLoad.setMaximumSize(QSize(100, 30))
        self.pushButtonLoad.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon = QIcon(":/icons/email_open.png")
        icon.addFile(
            ":/icons/email_open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.pushButtonLoad.setIcon(icon)
        self.pushButtonLoad.setFlat(False)
        self.horizontalLayoutCTA.addWidget(self.pushButtonLoad)

        self.horizontalSpacerCTARight = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayoutCTA.addItem(self.horizontalSpacerCTARight)

        self.gridLayoutMain.addLayout(self.horizontalLayoutCTA, 3, 0, 1, 1)

    def retranslateUi(self, WelcomeFrame):
        WelcomeFrame.setWindowTitle(
            QCoreApplication.translate("WelcomeFrame", "Frame", None)
        )
        self.labelLogo.setText("")
        self.pushButtonLoad.setText(
            QCoreApplication.translate("WelcomeFrame", "Load File", None)
        )
        self.labelWelcomeTo.setText(
            QCoreApplication.translate("WelcomeFrame", "Welcome to", None)
        )
        self.labelAppName.setText(
            QCoreApplication.translate("WelcomeFrame", "py-mailbox-viewer", None)
        )
        self.labelDesc.setText(
            QCoreApplication.translate(
                "WelcomeFrame", "Load a mail file to get started", None
            )
        )
