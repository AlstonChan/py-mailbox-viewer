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
        self.gridLayout_2 = QGridLayout(WelcomeFrame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayoutMain = QGridLayout()
        self.gridLayoutMain.setObjectName("gridLayoutMain")
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

        self.label_3 = QLabel(WelcomeFrame)
        self.label_3.setObjectName("label_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(17)
        self.label_3.setFont(font)
        self.label_3.setPixmap(QPixmap(":/icons/logo.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )

        self.horizontalLayoutLogo.addWidget(self.label_3)

        self.horizontalSpacerLogoRight = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayoutLogo.addItem(self.horizontalSpacerLogoRight)

        self.gridLayoutMain.addLayout(self.horizontalLayoutLogo, 1, 0, 1, 1)

        self.horizontalLayoutCTA = QHBoxLayout()
        self.horizontalLayoutCTA.setObjectName("horizontalLayoutCTA")
        self.horizontalSpacerCTALeft = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayoutCTA.addItem(self.horizontalSpacerCTALeft)

        self.pushButtonLoad = QPushButton(WelcomeFrame)
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        sizePolicy1.setHorizontalStretch(76)
        sizePolicy1.setVerticalStretch(30)
        sizePolicy1.setHeightForWidth(
            self.pushButtonLoad.sizePolicy().hasHeightForWidth()
        )
        self.pushButtonLoad.setSizePolicy(sizePolicy1)
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

        self.verticalSpacerTop = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayoutMain.addItem(self.verticalSpacerTop, 0, 0, 1, 1)

        self.verticalLayoutText = QVBoxLayout()
        self.verticalLayoutText.setObjectName("verticalLayoutText")
        self.verticalLayoutText.setContentsMargins(-1, 10, -1, 10)
        self.horizontalLayoutTitle = QHBoxLayout()
        self.horizontalLayoutTitle.setObjectName("horizontalLayoutTitle")
        self.horizontalSpacerTitleLeft = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayoutTitle.addItem(self.horizontalSpacerTitleLeft)

        self.labelWelcomeTo = QLabel(WelcomeFrame)
        self.labelWelcomeTo.setObjectName("labelWelcomeTo")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.labelWelcomeTo.sizePolicy().hasHeightForWidth()
        )
        self.labelWelcomeTo.setSizePolicy(sizePolicy2)
        self.labelWelcomeTo.setFont(font)
        self.labelWelcomeTo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutTitle.addWidget(self.labelWelcomeTo)

        self.labelAppName = QLabel(WelcomeFrame)
        self.labelAppName.setObjectName("labelAppName")
        sizePolicy2.setHeightForWidth(
            self.labelAppName.sizePolicy().hasHeightForWidth()
        )
        self.labelAppName.setSizePolicy(sizePolicy2)
        font1 = QFont()
        font1.setFamilies(["STSong"])
        font1.setPointSize(17)
        font1.setBold(True)
        self.labelAppName.setFont(font1)
        self.labelAppName.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutTitle.addWidget(self.labelAppName)

        self.horizontalSpacerTitleRight = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayoutTitle.addItem(self.horizontalSpacerTitleRight)

        self.verticalLayoutText.addLayout(self.horizontalLayoutTitle)

        self.labelDesc = QLabel(WelcomeFrame)
        self.labelDesc.setObjectName("labelDesc")
        font2 = QFont()
        font2.setPointSize(11)
        self.labelDesc.setFont(font2)
        self.labelDesc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutText.addWidget(self.labelDesc)

        self.gridLayoutMain.addLayout(self.verticalLayoutText, 2, 0, 1, 1)

        self.verticalSpacerBottom = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayoutMain.addItem(self.verticalSpacerBottom, 4, 0, 1, 1)

        self.gridLayoutMain.setRowMinimumHeight(3, 40)

        self.gridLayout_2.addLayout(self.gridLayoutMain, 0, 0, 1, 1)

        self.retranslateUi(WelcomeFrame)

        self.pushButtonLoad.setDefault(True)

        QMetaObject.connectSlotsByName(WelcomeFrame)

    # setupUi

    def retranslateUi(self, WelcomeFrame):
        WelcomeFrame.setWindowTitle(
            QCoreApplication.translate("WelcomeFrame", "Frame", None)
        )
        self.label_3.setText("")
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

    # retranslateUi
