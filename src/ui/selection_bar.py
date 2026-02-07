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
    Qt,
)
from PySide6.QtGui import (
    QFont,
)
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


class Ui_SelectionBarWidget(object):
    def setupUi(self, SelectionBarWidget):
        if not SelectionBarWidget.objectName():
            SelectionBarWidget.setObjectName("SelectionBarWidget")

        self._setup_base_widget_properties(SelectionBarWidget)
        self._setup_main_frame_and_layouts(
            SelectionBarWidget
        )  # This method will setup frameMain and all layouts
        self._setup_labels(SelectionBarWidget)

    def _setup_base_widget_properties(self, SelectionBarWidget):
        SelectionBarWidget.setWindowModality(Qt.WindowModality.NonModal)
        SelectionBarWidget.resize(330, 56)
        SelectionBarWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        SelectionBarWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

    def _setup_main_frame_and_layouts(self, SelectionBarWidget):
        # Setup gridLayout first, as frameMain will be added to it
        self.gridLayout = QGridLayout(SelectionBarWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # Setup frameMain
        self.frameMain = QFrame(SelectionBarWidget)
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

    def _setup_labels(self, SelectionBarWidget):
        font = QFont()
        font.setPointSize(9)

        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)

        # Label Recipient
        self.labelRecipient = QLabel(self.frameMain)
        self.labelRecipient.setObjectName("labelRecipient")
        sizePolicy1.setHeightForWidth(
            self.labelRecipient.sizePolicy().hasHeightForWidth()
        )
        self.labelRecipient.setSizePolicy(sizePolicy1)
        self.labelRecipient.setFont(font)
        self.labelRecipient.setAutoFillBackground(False)
        self.labelRecipient.setWordWrap(True)
        self.labelRecipient.setMargin(0)
        self.labelRecipient.setText("Name <email>")  # Set text directly
        self.hBoxLayoutTop.addWidget(self.labelRecipient)

        # Label DateTime
        self.labelDateTime = QLabel(self.frameMain)
        self.labelDateTime.setObjectName("labelDateTime")
        sizePolicy = (
            QSizePolicy(  # This sizePolicy is locally defined, matching original code
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
            )
        )
        sizePolicy.setHeightForWidth(
            self.labelDateTime.sizePolicy().hasHeightForWidth()
        )
        self.labelDateTime.setSizePolicy(sizePolicy)
        self.labelDateTime.setFont(font)
        self.labelDateTime.setText("00:00 PM")  # Set text directly
        self.hBoxLayoutTop.addWidget(self.labelDateTime)

        self.formLayout.setLayout(
            0, QFormLayout.ItemRole.SpanningRole, self.hBoxLayoutTop
        )
        self.formLayout.setItem(
            1, QFormLayout.ItemRole.SpanningRole, self.spacerVertical
        )

        # Label Subject
        self.labelSubject = QLabel(self.frameMain)
        self.labelSubject.setObjectName("labelSubject")
        sizePolicy1.setHeightForWidth(
            self.labelSubject.sizePolicy().hasHeightForWidth()
        )
        self.labelSubject.setSizePolicy(sizePolicy1)
        self.labelSubject.setFont(font)
        self.labelSubject.setAutoFillBackground(False)
        self.labelSubject.setWordWrap(True)
        self.labelSubject.setMargin(0)
        self.labelSubject.setText("Email Subject")  # Set text directly
        self.hBoxLayoutBottom.addWidget(self.labelSubject)

        # Label Size
        self.labelSize = QLabel(self.frameMain)
        self.labelSize.setObjectName("labelSize")
        sizePolicy = (
            QSizePolicy(  # This sizePolicy is locally defined, matching original code
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
            )
        )
        sizePolicy.setHeightForWidth(self.labelSize.sizePolicy().hasHeightForWidth())
        self.labelSize.setSizePolicy(sizePolicy)
        self.labelSize.setFont(font)
        self.labelSize.setText("7KB")  # Set text directly
        self.hBoxLayoutBottom.addWidget(self.labelSize)

        self.formLayout.setLayout(
            2, QFormLayout.ItemRole.SpanningRole, self.hBoxLayoutBottom
        )
