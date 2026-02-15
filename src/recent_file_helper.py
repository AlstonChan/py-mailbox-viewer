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

from typing import List
from PySide6.QtCore import QSettings
from logger_config import logger

RECENT_FILES_KEY = "recentFiles"
MAX_RECENT_FILES = 10


class RecentFileHelper:
    def __init__(self):
        # QSettings automatically uses the organization name and application name
        # set by QCoreApplication.setOrganizationName and setApplicationName.
        # These are set in app.py.
        self.settings = QSettings()

    def add_recent_file(self, file_path: str):
        """
        Adds a file path to the list of recent files.
        If the file is already in the list, it's moved to the top.
        If the list exceeds MAX_RECENT_FILES, the oldest entry is removed.
        """
        recent_files = self.get_recent_files()

        if file_path in recent_files:
            recent_files.remove(file_path)

        recent_files.insert(0, file_path)  # Add to top

        # Trim list if it exceeds max size
        if len(recent_files) > MAX_RECENT_FILES:
            recent_files = recent_files[:MAX_RECENT_FILES]

        self.settings.setValue(RECENT_FILES_KEY, recent_files)
        logger.debug(
            f"Added '{file_path}' to recent files. Current list: {recent_files}"
        )

    def get_recent_files(self) -> List[str]:
        """
        Retrieves the list of recent file paths.
        """
        # QSettings.value returns a QVariant, which for string lists
        # will convert to a Python list of strings automatically.
        # The second argument is a default value if the key doesn't exist.
        # QSettings returns an empty list if the key doesn't exist and the default is an empty list,
        # but it returns a list of QVariants, so we explicitly convert to list of strings.
        value = self.settings.value(RECENT_FILES_KEY, [])
        if isinstance(
            value, str
        ):  # Handle case where it might be a single string if only one item was saved
            return [value] if value else []
        return [str(item) for item in value] if isinstance(value, list) else []

    def remove_file(self, file_path: str):
        """
        Removes a specific file path from the list of recent files.
        """
        recent_files = self.get_recent_files()
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.settings.setValue(RECENT_FILES_KEY, recent_files)

    def clear_recent_files(self):
        """
        Clears all recent file paths.
        """
        self.settings.remove(RECENT_FILES_KEY)
