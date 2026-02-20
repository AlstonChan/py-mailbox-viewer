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

"""
A virtual-scrolling list that only materialises SelectionBarWidget instances
for the rows currently visible in the viewport (plus a small buffer).

This keeps the widget count constant (~20-30) regardless of how many
emails are loaded, eliminating the multi-second freeze that occurred when
creating thousands of widgets at once.
"""

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QWidget,
)

from mail_message import MailMessage
from ui.selection_bar import SelectionBarWidget
from logger_config import logger

# How many extra rows to render above/below the visible area
_BUFFER_ROWS = 4
# Padding at the top of the viewport before the first row
_TOP_PADDING = 4


class VirtualSelectionBarList(QAbstractScrollArea):
    """Virtualised list that recycles a small pool of SelectionBarWidget
    instances to display an arbitrarily large list of MailMessage objects.

    Signals:
        itemClicked(int): emitted with the *logical* email index when
                          a selection bar is clicked.
    """

    itemClicked = Signal(int)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Data
        self._emails: List[MailMessage] = []
        self._row_height: int = 0  # measured once from a prototype widget
        self._active_index: Optional[int] = None

        # Pool of recycled widgets – keyed by logical row index currently
        # assigned.  value = (row_index, widget)
        self._pool: dict[int, SelectionBarWidget] = {}

        # Appearance
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # The viewport itself needs a layout-less background
        self.viewport().setStyleSheet(
            "background-color: palette(shadow);" "border-radius: 10px;"
        )

        # Measure row height from a temporary prototype
        self._measure_row_height()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_emails(self, emails: List[MailMessage]) -> None:
        """Replace the entire data set and refresh the view."""
        self._emails = emails
        self._active_index = None
        self._recycle_all()
        self._update_scrollbar()
        self._layout_visible()

    def set_active_index(self, index: Optional[int]) -> None:
        """Highlight *index* as the currently selected row."""
        prev = self._active_index
        self._active_index = index

        # Update styling on widgets that are currently materialised
        if prev is not None and prev in self._pool:
            self._pool[prev].set_active(False)
        if index is not None and index in self._pool:
            self._pool[index].set_active(True)

    def get_active_index(self) -> Optional[int]:
        return self._active_index

    def scroll_to_index(self, index: int) -> None:
        """Ensure *index* is visible with one row of context above/below."""
        if not self._emails or index < 0 or index >= len(self._emails):
            return
        vbar = self.verticalScrollBar()
        vp_h = self.viewport().height()
        current = vbar.value()

        # Top/bottom pixel positions of the target row (including top padding)
        item_top = _TOP_PADDING + index * self._row_height
        item_bottom = item_top + self._row_height

        # One row of context above: if the row above would be clipped, scroll up
        context_top = item_top - self._row_height
        if context_top < current:
            vbar.setValue(max(0, context_top))
        # One row of context below: if the row below would be clipped, scroll down
        else:
            context_bottom = item_bottom + self._row_height
            if context_bottom > current + vp_h:
                vbar.setValue(context_bottom - vp_h)
        # else already comfortably visible – do nothing

    def email_count(self) -> int:
        return len(self._emails)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _measure_row_height(self) -> None:
        """Create a throw-away SelectionBarWidget to find out how tall one row is."""
        proto = SelectionBarWidget(0, None)
        proto.adjustSize()
        h = proto.sizeHint().height()
        self._row_height = max(h, 30) + 5
        proto.deleteLater()

    def _update_scrollbar(self) -> None:
        total_height = _TOP_PADDING + len(self._emails) * self._row_height
        vp_h = self.viewport().height()
        vbar = self.verticalScrollBar()
        vbar.setRange(0, max(0, total_height - vp_h))
        vbar.setPageStep(vp_h)
        vbar.setSingleStep(self._row_height)

    def _visible_range(self):
        """Return (first_row, last_row_exclusive) that should be rendered."""
        if not self._emails:
            return 0, 0
        vbar = self.verticalScrollBar()
        scroll_y = vbar.value()
        vp_h = self.viewport().height()

        first = max(0, scroll_y // self._row_height - _BUFFER_ROWS)
        last = min(
            len(self._emails),
            (scroll_y + vp_h) // self._row_height + 1 + _BUFFER_ROWS,
        )
        return first, last

    def _recycle_all(self) -> None:
        """Hide and remove all pooled widgets."""
        for w in self._pool.values():
            w.hide()
            w.deleteLater()
        self._pool.clear()

    def _layout_visible(self) -> None:
        """Create / reposition widgets for the currently visible rows."""
        if not self._emails:
            return

        first, last = self._visible_range()
        needed = set(range(first, last))

        # 1. Remove widgets that scrolled out of range
        stale = [idx for idx in self._pool if idx not in needed]
        for idx in stale:
            w = self._pool.pop(idx)
            w.hide()
            w.deleteLater()

        # 2. Create widgets for newly visible rows
        scroll_y = self.verticalScrollBar().value()
        vp_w = self.viewport().width()
        margin = 4  # left/right padding inside the viewport

        for row in range(first, last):
            if row in self._pool:
                # Already exists – just reposition
                w = self._pool[row]
            else:
                # Create a new widget
                w = SelectionBarWidget(row, self.viewport())
                w.set_email_data(self._emails[row])
                w.clicked.connect(self._on_item_clicked)
                if row == self._active_index:
                    w.set_active(True)
                self._pool[row] = w

            y = _TOP_PADDING + row * self._row_height - scroll_y
            w.setGeometry(margin, y, vp_w - 2 * margin, self._row_height - 5)
            w.show()

    def _on_item_clicked(self, index: int) -> None:
        self.itemClicked.emit(index)

    # ------------------------------------------------------------------
    # Qt overrides
    # ------------------------------------------------------------------
    def scrollContentsBy(self, dx: int, dy: int) -> None:
        # Called by QAbstractScrollArea when the scrollbar moves
        self._layout_visible()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_scrollbar()
        self._layout_visible()

    def paintEvent(self, event) -> None:
        # We don't paint anything ourselves — the child widgets do the job.
        # But we must override to prevent QAbstractScrollArea from filling
        # the viewport with the default background.
        pass

    def wheelEvent(self, event) -> None:
        # Forward wheel events to the vertical scrollbar
        vbar = self.verticalScrollBar()
        delta = event.angleDelta().y()
        vbar.setValue(vbar.value() - delta)
        event.accept()
