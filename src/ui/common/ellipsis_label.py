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

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics


class EllipsisLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        super().setText(text)
        self.setMinimumWidth(1)

    def setText(self, text: str):
        self._text = text
        self._update_elide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elide()

    def _update_elide(self):
        if not self._text:
            super().setText("")
            return

        rect = self.contentsRect()
        if rect.width() <= 0:
            return

        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(
            self._text, Qt.TextElideMode.ElideRight, rect.width()
        )

        super().setText(elided)
