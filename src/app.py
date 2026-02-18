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

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from main import MainWindow
import resources_rc

from PySide6.QtCore import QCoreApplication
from constants import APP_NAME

QCoreApplication.setOrganizationName(APP_NAME)
QCoreApplication.setApplicationName(APP_NAME)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/logo.png"))
    window = MainWindow()
    window.setWindowIcon(QIcon(":/icons/logo.png"))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
