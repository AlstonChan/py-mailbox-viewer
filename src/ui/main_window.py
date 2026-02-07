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
    QRect,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QAction,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QMenu,
    QMenuBar,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QTextEdit,
)
from constants import APP_NAME


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")

        MainWindow.setWindowTitle(f"{APP_NAME} v1.0.0")
        MainWindow.resize(1200, 650)

        self._setup_actions(MainWindow)
        self._setup_central_widget(MainWindow)
        self._setup_menu_bar(MainWindow)
        self._setup_status_bar(MainWindow)

        self.tabMailBody.setCurrentIndex(0)

    def _setup_actions(self, MainWindow):
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setText("Open")

        self.actionReload = QAction(MainWindow)
        self.actionReload.setObjectName("actionReload")
        self.actionReload.setText("Reload")

        self.actionRecent_Files = QAction(MainWindow)
        self.actionRecent_Files.setObjectName("actionRecent_Files")
        self.actionRecent_Files.setText("Recent Files")

        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setText("Exit")

        self.actionSearch = QAction(MainWindow)
        self.actionSearch.setObjectName("actionSearch")
        self.actionSearch.setText("Search")

        self.actionFilter = QAction(MainWindow)
        self.actionFilter.setObjectName("actionFilter")
        self.actionFilter.setText("Filter")

        self.actionExport_Email = QAction(MainWindow)
        self.actionExport_Email.setObjectName("actionExport_Email")
        self.actionExport_Email.setText("Export Email")

        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout.setText("About")

        self.actionShortcuts = QAction(MainWindow)
        self.actionShortcuts.setObjectName("actionShortcuts")
        self.actionShortcuts.setText("Shortcuts")

        self.actionGitHub = QAction(MainWindow)
        self.actionGitHub.setObjectName("actionGitHub")
        self.actionGitHub.setText("GitHub")

        self.actionToggle_preview_pane = QAction(MainWindow)
        self.actionToggle_preview_pane.setObjectName("actionToggle_preview_pane")
        self.actionToggle_preview_pane.setText("Toggle preview pane")

        self.actionZoom_in_out = QAction(MainWindow)
        self.actionZoom_in_out.setObjectName("actionZoom_in_out")
        self.actionZoom_in_out.setText("Zoom in / out")

        self.actionShow_headers = QAction(MainWindow)
        self.actionShow_headers.setObjectName("actionShow_headers")
        self.actionShow_headers.setText("Show headers")

        self.actionWrap_text = QAction(MainWindow)
        self.actionWrap_text.setObjectName("actionWrap_text")
        self.actionWrap_text.setText("Wrap text")

    def _setup_central_widget(self, MainWindow):
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName("centralwidget")

        self.centralWidgetGridLayout = QGridLayout(self.central_widget)
        self.centralWidgetGridLayout.setObjectName("centralWidgetGridLayout")

        self.splitterMain = QSplitter(self.central_widget)
        self.splitterMain.setObjectName("splitterMain")
        mainSplitterSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        mainSplitterSizePolicy.setHorizontalStretch(100)
        mainSplitterSizePolicy.setVerticalStretch(0)
        mainSplitterSizePolicy.setHeightForWidth(
            self.splitterMain.sizePolicy().hasHeightForWidth()
        )
        self.splitterMain.setSizePolicy(mainSplitterSizePolicy)
        self.splitterMain.setOrientation(Qt.Orientation.Horizontal)

        self._setup_left_panel(MainWindow)
        self._setup_right_panel(MainWindow)

        self.centralWidgetGridLayout.addWidget(self.splitterMain, 0, 0, 1, 1)
        self.splitterMain.setSizes([700, 900])
        MainWindow.setCentralWidget(self.central_widget)

    def _setup_left_panel(self, MainWindow):
        self.scrollAreaLeft = QScrollArea(self.splitterMain)
        self.scrollAreaLeft.setObjectName("scrollAreaLeft")
        leftScrollAreaSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # leftScrollAreaSizePolicy.setHorizontalStretch(2)
        leftScrollAreaSizePolicy.setVerticalStretch(2)
        leftScrollAreaSizePolicy.setHeightForWidth(
            self.scrollAreaLeft.sizePolicy().hasHeightForWidth()
        )
        self.scrollAreaLeft.setSizePolicy(leftScrollAreaSizePolicy)
        self.scrollAreaLeft.setMinimumSize(QSize(150, 0))
        self.scrollAreaLeft.setWidgetResizable(True)
        self.scrollAreaLeft.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 198, 601))
        scrollAreaWidgetContentsSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        scrollAreaWidgetContentsSizePolicy.setHorizontalStretch(1)
        scrollAreaWidgetContentsSizePolicy.setVerticalStretch(0)
        scrollAreaWidgetContentsSizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.scrollAreaWidgetContents.setSizePolicy(scrollAreaWidgetContentsSizePolicy)
        self.scrollAreaLeft.setWidget(self.scrollAreaWidgetContents)
        self.splitterMain.addWidget(self.scrollAreaLeft)

        self.scrollAreaWidgetContents.setStyleSheet(
            """
                QWidget#scrollAreaWidgetContents {
                    background-color: palette(shadow);
                    border-radius: 10px;
                    border: 1px solid palette(mid);
                }
            """
        )

        # Initialize selectionBarLayout here or in a dedicated setup method
        self.selectionBarLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.selectionBarLayout.setContentsMargins(4, 4, 4, 4)
        self.selectionBarLayout.setSpacing(5)  # Add some spacing between selection bars

    def _setup_right_panel(self, MainWindow):
        self.frameRight = QFrame(self.splitterMain)
        self.frameRight.setObjectName("frameRight")
        rightFrameSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        # rightFrameSizePolicy.setHorizontalStretch(0)
        rightFrameSizePolicy.setVerticalStretch(0)
        rightFrameSizePolicy.setHeightForWidth(
            self.frameRight.sizePolicy().hasHeightForWidth()
        )
        self.frameRight.setSizePolicy(rightFrameSizePolicy)
        self.frameRight.setFrameShape(QFrame.Shape.StyledPanel)
        self.frameRight.setFrameShadow(QFrame.Shadow.Raised)
        self.rightFrameGridLayout = QGridLayout(self.frameRight)
        self.rightFrameGridLayout.setObjectName("rightFrameGridLayout")
        self.rightFrameGridLayout.setContentsMargins(0, 0, 0, 0)

        self._setup_email_splitter(MainWindow)

        self.rightFrameGridLayout.addWidget(self.splitterEmail, 0, 0, 1, 1)
        self.splitterMain.addWidget(self.frameRight)

    def _setup_email_splitter(self, MainWindow):
        self.splitterEmail = QSplitter(self.frameRight)
        self.splitterEmail.setObjectName("splitterEmail")
        self.splitterEmail.setOrientation(Qt.Orientation.Vertical)

        # Setup Mail Header Frame
        self.frameMailHeader = QFrame(self.splitterEmail)
        self.frameMailHeader.setObjectName("frameMailHeader")
        mailHeaderFrameSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        mailHeaderFrameSizePolicy.setHorizontalStretch(0)
        mailHeaderFrameSizePolicy.setVerticalStretch(25)
        mailHeaderFrameSizePolicy.setHeightForWidth(
            self.frameMailHeader.sizePolicy().hasHeightForWidth()
        )
        self.frameMailHeader.setSizePolicy(mailHeaderFrameSizePolicy)
        self.frameMailHeader.setMinimumSize(QSize(200, 20))
        self.frameMailHeader.setFrameShape(QFrame.Shape.StyledPanel)
        self.frameMailHeader.setFrameShadow(QFrame.Shadow.Plain)
        self.splitterEmail.addWidget(self.frameMailHeader)

        # Setup Mail Body Tabs
        self.tabMailBody = QTabWidget(self.splitterEmail)
        self.tabMailBody.setObjectName("tabMailBody")
        mailBodyTabSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        mailBodyTabSizePolicy.setHorizontalStretch(0)
        mailBodyTabSizePolicy.setVerticalStretch(75)
        mailBodyTabSizePolicy.setHeightForWidth(
            self.tabMailBody.sizePolicy().hasHeightForWidth()
        )
        self.tabMailBody.setSizePolicy(mailBodyTabSizePolicy)
        self.tabMailBody.setMinimumSize(QSize(200, 20))
        self.tabMailBody.setTabShape(QTabWidget.TabShape.Rounded)

        # Setup HTML Tab
        self.tabHtml = QWidget()
        self.tabHtml.setObjectName("tabHtml")
        self.tabMailBody.addTab(self.tabHtml, "HTML")
        self.htmlBodyLayout = QVBoxLayout(self.tabHtml)
        self.htmlBodyLayout.setObjectName("htmlBodyLayout")
        self.htmlBodyLayout.setContentsMargins(0, 0, 0, 0)
        self.textEditHtml = QTextEdit(self.tabHtml)
        self.textEditHtml.setObjectName("textEditHtml")
        self.textEditHtml.setReadOnly(True)
        self.textEditHtml.setContentsMargins(0, 0, 0, 0)
        self.htmlBodyLayout.addWidget(self.textEditHtml)

        # Setup Plain Text Tab
        self.tabPlainText = QWidget()
        self.tabPlainText.setObjectName("tabPlainText")
        self.tabMailBody.addTab(self.tabPlainText, "Plain")
        self.plainTextBodyLayout = QVBoxLayout(self.tabPlainText)
        self.plainTextBodyLayout.setObjectName("plainTextBodyLayout")
        self.plainTextBodyLayout.setContentsMargins(0, 0, 0, 0)
        self.textEditPlain = QTextEdit(self.tabPlainText)
        self.textEditPlain.setObjectName("textEditPlain")
        self.textEditPlain.setReadOnly(True)
        self.textEditPlain.setContentsMargins(0, 0, 0, 0)
        self.plainTextBodyLayout.addWidget(self.textEditPlain)

        # Setup Raw MIME Tab
        self.tabRawMime = QWidget()
        self.tabRawMime.setObjectName("tabRawMime")
        self.tabMailBody.addTab(self.tabRawMime, "Raw")
        self.rawMimeBodyLayout = QVBoxLayout(self.tabRawMime)
        self.rawMimeBodyLayout.setObjectName("rawMimeBodyLayout")
        self.rawMimeBodyLayout.setContentsMargins(0, 0, 0, 0)
        self.textEditRaw = QTextEdit(self.tabRawMime)
        self.textEditRaw.setObjectName("textEditRaw")
        self.textEditRaw.setReadOnly(True)
        self.textEditRaw.setContentsMargins(0, 0, 0, 0)
        self.rawMimeBodyLayout.addWidget(self.textEditRaw)

        self.splitterEmail.addWidget(self.tabMailBody)
        self.splitterEmail.setSizes([400, 900])

    def _setup_menu_bar(self, MainWindow):
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 907, 22))

        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")

        self.menuTool = QMenu(self.menubar)
        self.menuTool.setObjectName("menuTool")
        self.menuTool.setTitle("Tool")

        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuHelp.setTitle("Help")

        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuView.setTitle("View")

        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTool.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionReload)
        self.menuFile.addAction(self.actionRecent_Files)
        self.menuFile.addAction(self.actionExit)

        self.menuTool.addAction(self.actionSearch)
        self.menuTool.addAction(self.actionFilter)
        self.menuTool.addSeparator()
        self.menuTool.addAction(self.actionExport_Email)

        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionShortcuts)

        self.menuView.addAction(self.actionToggle_preview_pane)
        self.menuView.addAction(self.actionZoom_in_out)
        self.menuView.addAction(self.actionShow_headers)
        self.menuView.addAction(self.actionWrap_text)

    def _setup_status_bar(self, MainWindow):
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
