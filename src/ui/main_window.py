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
from typing import Callable, Sequence
from PySide6.QtCore import QRect, QSize, Qt, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QMenu,
    QMenuBar,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QHBoxLayout,
    QSpacerItem,
    QToolButton,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from constants import APP_NAME
from ui.mail_header import MailHeaderWidget
from ui.welcome_screen import WelcomeFrame
from logger_config import logger


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
        self.actionOpen.setIcon(QIcon(":/icons/email_open.png"))
        self.actionOpen.setShortcut(QKeySequence("Ctrl+O"))

        self.actionReload = QAction(MainWindow)
        self.actionReload.setObjectName("actionReload")
        self.actionReload.setText("Reload")
        self.actionReload.setIcon(QIcon(":/icons/arrow_refresh.png"))
        self.actionReload.setShortcut(QKeySequence("Ctrl+R"))

        self.actionRecent_Files = QMenu(MainWindow)
        self.actionRecent_Files.setObjectName("actionRecent_Files")
        self.actionRecent_Files.setTitle("Recent Files")
        self.actionRecent_Files.setIcon(QIcon(":/icons/mail_yellow.png"))

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
        self.actionAbout.setIcon(QIcon(":/icons/information.png"))
        self.actionAbout.setShortcut(QKeySequence("F1"))

        self.actionShortcuts = QAction(MainWindow)
        self.actionShortcuts.setObjectName("actionShortcuts")
        self.actionShortcuts.setText("Shortcuts")

        self.actionToggle_preview_pane = QAction(MainWindow)
        self.actionToggle_preview_pane.setObjectName("actionToggle_preview_pane")
        self.actionToggle_preview_pane.setText("Toggle preview pane")

        self.actionZoom_in_out = QAction(MainWindow)
        self.actionZoom_in_out.setObjectName("actionZoom_in_out")
        self.actionZoom_in_out.setText("Zoom in / out")
        self.actionZoom_in_out.setIcon(QIcon(":/icons/zoom.png"))

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
        self.leftPanelWidget = QWidget(self.splitterMain)
        self.leftPanelWidget.setObjectName("leftPanelWidget")
        self.verticalLayoutLeft = QVBoxLayout(self.leftPanelWidget)
        self.verticalLayoutLeft.setObjectName("verticalLayoutLeft")
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutLeft.setSpacing(0)

        self.toolbarFrame = QFrame(self.leftPanelWidget)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolbarFrame.sizePolicy().hasHeightForWidth())

        self.toolbarFrame.setSizePolicy(sizePolicy)
        self.toolbarFrame.setMinimumSize(QSize(0, 35))
        self.toolbarFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.toolbarFrame.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout = QHBoxLayout(self.toolbarFrame)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalSpacer = QSpacerItem(
            165, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButton = QToolButton(self.toolbarFrame)
        self.toolButton.setObjectName("toolButton")
        self.toolButton.setIcon(QIcon(":/icons/sort.png"))
        self.toolButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toolButton.setStyleSheet(
            """
            QToolButton {
                padding: 3px;
                border: 1px solid transparent;
                border-radius: 4px;
                background: transparent;
            }
            QToolButton:hover {
                border: 1px solid palette(mid);
                background-color: palette(button);
            }
            QToolButton:pressed {
                background-color: palette(midlight);
            }
            QToolButton::menu-indicator {
                image: none;
            }
            """
        )

        self._setup_sort_menu(MainWindow)

        self.horizontalLayout.addWidget(self.toolButton)

        self.verticalLayoutLeft.addWidget(self.toolbarFrame)

        self.scrollAreaLeft = QScrollArea(self.leftPanelWidget)
        leftScrollAreaSizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
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
        self.verticalLayoutLeft.addWidget(self.scrollAreaLeft)

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

        self.splitterMain.addWidget(self.leftPanelWidget)

    def _setup_sort_menu(self, MainWindow):
        self.sortMenu = QMenu(self.toolButton)
        self.sortMenu.setObjectName("sortMenu")

        # Sort field actions (mutually exclusive)
        self.sortFieldGroup = QActionGroup(MainWindow)
        self.sortFieldGroup.setExclusive(True)

        self.actionSortByDate = QAction("Date", MainWindow)
        self.actionSortByDate.setObjectName("actionSortByDate")
        self.actionSortByDate.setCheckable(True)
        self.actionSortByDate.setChecked(True)
        self.sortFieldGroup.addAction(self.actionSortByDate)

        self.actionSortBySize = QAction("Size", MainWindow)
        self.actionSortBySize.setObjectName("actionSortBySize")
        self.actionSortBySize.setCheckable(True)
        self.sortFieldGroup.addAction(self.actionSortBySize)

        self.actionSortByTo = QAction("To", MainWindow)
        self.actionSortByTo.setObjectName("actionSortByTo")
        self.actionSortByTo.setCheckable(True)
        self.sortFieldGroup.addAction(self.actionSortByTo)

        self.actionSortByFrom = QAction("From", MainWindow)
        self.actionSortByFrom.setObjectName("actionSortByFrom")
        self.actionSortByFrom.setCheckable(True)
        self.sortFieldGroup.addAction(self.actionSortByFrom)

        self.actionSortBySubject = QAction("Subject", MainWindow)
        self.actionSortBySubject.setObjectName("actionSortBySubject")
        self.actionSortBySubject.setCheckable(True)
        self.sortFieldGroup.addAction(self.actionSortBySubject)

        self.sortMenu.addAction(self.actionSortByDate)
        self.sortMenu.addAction(self.actionSortBySize)
        self.sortMenu.addAction(self.actionSortByTo)
        self.sortMenu.addAction(self.actionSortByFrom)
        self.sortMenu.addAction(self.actionSortBySubject)

        # Separator
        self.sortMenu.addSeparator()

        # Sort order actions (mutually exclusive)
        self.sortOrderGroup = QActionGroup(MainWindow)
        self.sortOrderGroup.setExclusive(True)

        self.actionSortAscending = QAction("Ascending", MainWindow)
        self.actionSortAscending.setObjectName("actionSortAscending")
        self.actionSortAscending.setCheckable(True)

        self.sortOrderGroup.addAction(self.actionSortAscending)
        self.actionSortDescending = QAction("Descending", MainWindow)
        self.actionSortDescending.setObjectName("actionSortDescending")
        self.actionSortDescending.setCheckable(True)
        self.actionSortDescending.setChecked(True)
        self.sortOrderGroup.addAction(self.actionSortDescending)

        self.sortMenu.addAction(self.actionSortAscending)
        self.sortMenu.addAction(self.actionSortDescending)

        self.toolButton.setMenu(self.sortMenu)

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

        # Stacked widget to switch between welcome screen and email detail view
        self.rightStackedWidget = QStackedWidget(self.frameRight)
        self.rightStackedWidget.setObjectName("rightStackedWidget")

        # Page 0: Welcome screen
        self.welcomeFrame = QFrame()
        self.welcomeFrame.setObjectName("welcomeFrame")
        self.welcomeUi = WelcomeFrame()
        self.welcomeUi.setupUi(self.welcomeFrame)
        self.rightStackedWidget.addWidget(self.welcomeFrame)

        # Page 1: Email detail view (header + body splitter)
        self._setup_email_splitter(MainWindow)
        self.rightStackedWidget.addWidget(self.splitterEmail)

        # Show welcome screen by default
        self.rightStackedWidget.setCurrentIndex(0)

        self.rightFrameGridLayout.addWidget(self.rightStackedWidget, 0, 0, 1, 1)
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

        self.mailHeaderLayout = QVBoxLayout(self.frameMailHeader)
        self.mailHeaderLayout.setObjectName("mailHeaderLayout")
        self.mailHeaderLayout.setContentsMargins(2, 2, 2, 2)
        self.mailHeaderScrollArea = QScrollArea(self.frameMailHeader)
        self.mailHeaderScrollArea.setWidgetResizable(True)
        self.mailHeaderScrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.mailHeaderScrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.mailHeaderScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.mailHeaderScrollArea.setStyleSheet(
            "QScrollArea { background-color: palette(base); border: none; }"
        )

        self.mailHeader = MailHeaderWidget()
        self.mailHeader.setStyleSheet(
            "MailHeaderWidget { background-color: palette(base); }"
        )
        self.mailHeaderScrollArea.setWidget(self.mailHeader)
        self.mailHeaderLayout.addWidget(self.mailHeaderScrollArea)

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
        self.webEngineViewHtml = QWebEngineView(self.tabHtml)
        self.webEngineViewHtml.setObjectName("webEngineViewHtml")
        self.webEngineViewHtml.setContentsMargins(1, 1, 1, 1)
        self.htmlBodyLayout.addWidget(self.webEngineViewHtml)

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
        self.splitterEmail.setSizes([440, 900])

    def _setup_menu_bar(self, MainWindow):
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 907, 22))

        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")

        # self.menuTool = QMenu(self.menubar)
        # self.menuTool.setObjectName("menuTool")
        # self.menuTool.setTitle("Tool")

        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuHelp.setTitle("Help")

        # self.menuView = QMenu(self.menubar)
        # self.menuView.setObjectName("menuView")
        # self.menuView.setTitle("View")

        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        # self.menubar.addAction(self.menuTool.menuAction())
        # self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionReload)
        self.menuFile.addAction(self.actionRecent_Files.menuAction())
        self.menuFile.addAction(self.actionExit)

        # self.menuTool.addAction(self.actionSearch)
        # self.menuTool.addAction(self.actionFilter)
        # self.menuTool.addSeparator()
        # self.menuTool.addAction(self.actionExport_Email)

        self.menuHelp.addAction(self.actionAbout)
        # self.menuHelp.addAction(self.actionShortcuts)

        # self.menuView.addAction(self.actionToggle_preview_pane)
        # self.menuView.addAction(self.actionZoom_in_out)
        # self.menuView.addAction(self.actionShow_headers)
        # self.menuView.addAction(self.actionWrap_text)

    def _setup_status_bar(self, MainWindow):
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

    def set_recent_files(
        self, recent_files: list[str], open_recent_file_callback: Callable[[str], None]
    ):
        logger.debug(f"Setting recent files menu with: {recent_files}")
        if (self.actionRecent_Files is None) or (
            not isinstance(self.actionRecent_Files, QMenu)
        ):
            return  # Safety check to ensure the menu exists before trying to modify it

        self.actionRecent_Files.clear()  # Clear existing actions
        if not recent_files or not open_recent_file_callback:
            logger.debug(
                "No recent files or callback provided, adding disabled 'No recent files' action"
            )
            no_recent_action = QAction(self.actionRecent_Files)
            no_recent_action.setText("No recent files")
            no_recent_action.setEnabled(False)
            self.actionRecent_Files.addAction(no_recent_action)
        else:
            for i, file_path in enumerate(recent_files):
                # Display only the filename if path is too long, otherwise full path
                display_text = f"&{i + 1}. {os.path.basename(file_path)}"
                action = QAction(self.actionRecent_Files)
                action.setText(display_text)
                action.setStatusTip(file_path)  # Show full path in status bar
                action.setShortcut(
                    QKeySequence(f"Ctrl+{i + 1}")
                )  # Add shortcut for quick access
                action.triggered.connect(
                    lambda checked, path=file_path: open_recent_file_callback(path)
                )
                self.actionRecent_Files.addAction(action)

    def ensure_selection_bar_visible(
        self, selection_bar_widgets: Sequence[QWidget], widget: QWidget, delta: int = 0
    ) -> None:
        """Scroll the left scroll area so the provided widget is visible.

        Behavior:
        - If navigating down (delta>0) and the newly selected widget is in the
          last two visible items, scroll down so one item remains visible below it.
        - If navigating up (delta<0) and the newly selected widget is in the
          first two visible items, scroll up so one item remains visible above it.
        - Otherwise, don't change the scroll (avoid unnecessary jumps).

        Scrolling is animated over ~100ms for smoother UX.

        Args:
            selection_bar_widgets: Sequence of all selection bar widgets
            widget: The widget to make visible
            delta: Direction of navigation (-1 for up, +1 for down, 0 for no navigation)
        """
        if not hasattr(self, "scrollAreaLeft") or widget is None:
            return
        try:
            scroll_widget = self.scrollAreaLeft.widget()
            if scroll_widget is None:
                return

            viewport = self.scrollAreaLeft.viewport()
            vbar = self.scrollAreaLeft.verticalScrollBar()
            vp_h = viewport.height()

            # Content coordinates for viewport visible range
            visible_top = vbar.value()
            visible_bottom = visible_top + vp_h

            # Compute positions of all selection widgets to determine visible index range
            tops = []
            for w in selection_bar_widgets:
                pos = w.mapTo(scroll_widget, QPoint(0, 0)).y()
                tops.append((w, pos, pos + w.height()))

            # Find first and last visible indices
            first_visible = None
            last_visible = None
            for idx, (_, top, bottom) in enumerate(tops):
                if bottom > visible_top and top < visible_bottom:
                    if first_visible is None:
                        first_visible = idx
                    last_visible = idx

            # If nothing visible, just return
            if first_visible is None or last_visible is None:
                return

            # Find index of the widget to show
            try:
                idx = selection_bar_widgets.index(widget)
            except ValueError:
                return

            do_scroll = False
            desired_v = visible_top

            # If moving down and widget is among the last two visible, scroll down
            if delta > 0 and idx >= (last_visible - 1):
                # Aim to position widget so one item remains visible below it
                # This means scrolling to make the widget appear second-from-bottom
                if idx < len(tops) - 1:
                    # Scroll so that widget is at position where next widget is partially visible
                    widget_top = tops[idx][1]
                    widget_bottom = tops[idx][2]
                    next_top = tops[idx + 1][1]
                    # Desired scroll: widget bottom is near viewport bottom, leaving space for one more
                    desired_v = widget_top - (
                        vp_h
                        - (tops[idx][2] - tops[idx][1])
                        - (tops[idx + 1][2] - tops[idx + 1][1])
                    )
                else:
                    # At last item, just scroll so it's fully visible at bottom
                    widget_top = tops[idx][1]
                    desired_v = widget_top - vp_h + (tops[idx][2] - tops[idx][1])
                do_scroll = True

            # If moving up and widget is among the first two visible, scroll up
            elif delta < 0 and idx <= (first_visible + 1):
                # Aim to position widget so one item is visible above it
                # This means making the widget appear second-from-top
                if idx > 0:
                    prev_top = tops[idx - 1][1]
                    # Scroll so previous widget is visible at top
                    desired_v = prev_top
                else:
                    # At first item, just scroll to top
                    desired_v = 0
                do_scroll = True

            # Clamp desired_v into scrollbar range
            desired_v = max(vbar.minimum(), min(vbar.maximum(), int(desired_v)))

            if do_scroll:
                # Animate scrollbar value for smooth UX, faster for up (200ms), slower for down (300ms)
                try:
                    duration = 200 if delta < 0 else 300
                    anim = QPropertyAnimation(vbar, b"value", self.scrollAreaLeft)
                    anim.setDuration(duration)
                    anim.setStartValue(vbar.value())
                    anim.setEndValue(desired_v)
                    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                    anim.start()
                    # Keep a reference to prevent garbage collection
                    if not hasattr(self, "_scroll_animations"):
                        self._scroll_animations = []
                    self._scroll_animations.append(anim)
                    # Clean up old animations
                    self._scroll_animations = [
                        a
                        for a in self._scroll_animations
                        if a.state() != a.State.Stopped
                    ]
                except Exception:
                    # Fallback to immediate set
                    vbar.setValue(desired_v)
        except Exception:
            logger.exception("Error while ensuring selection visible")

    def show_welcome_screen(self):
        """Switch the right panel to the welcome screen."""
        self.rightStackedWidget.setCurrentIndex(0)

    def show_email_detail_view(self):
        """Switch the right panel to the email detail view."""
        self.rightStackedWidget.setCurrentIndex(1)
