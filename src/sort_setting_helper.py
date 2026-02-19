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

from enum import Enum
from typing import Optional
from PySide6.QtCore import QSettings
from logger_config import logger

SORT_FIELD_KEY = "sort/field"
SORT_ORDER_KEY = "sort/order"


class SortField(str, Enum):
    DATE = "date"
    SIZE = "size"
    TO = "to"
    FROM = "from"
    SUBJECT = "subject"


class SortOrder(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


DEFAULT_SORT_FIELD = SortField.DATE
DEFAULT_SORT_ORDER = SortOrder.DESCENDING


class SortSettingHelper:
    _settings: Optional[QSettings] = None

    @classmethod
    def get_settings(cls) -> QSettings:
        """Returns the shared QSettings instance."""
        if cls._settings is None:
            cls._settings = QSettings()
        return cls._settings

    @classmethod
    def get_sort_field(cls) -> SortField:
        """Retrieves the saved sort field, defaulting to DATE."""
        value = cls.get_settings().value(SORT_FIELD_KEY, DEFAULT_SORT_FIELD.value)
        try:
            return SortField(value)
        except ValueError:
            logger.warning(f"Invalid sort field '{value}' in settings, using default.")
            return DEFAULT_SORT_FIELD

    @classmethod
    def set_sort_field(cls, field: SortField) -> None:
        """Saves the sort field to settings."""
        cls.get_settings().setValue(SORT_FIELD_KEY, field.value)
        logger.debug(f"Sort field set to: {field.value}")

    @classmethod
    def get_sort_order(cls) -> SortOrder:
        """Retrieves the saved sort order, defaulting to DESCENDING."""
        value = cls.get_settings().value(SORT_ORDER_KEY, DEFAULT_SORT_ORDER.value)
        try:
            return SortOrder(value)
        except ValueError:
            logger.warning(f"Invalid sort order '{value}' in settings, using default.")
            return DEFAULT_SORT_ORDER

    @classmethod
    def set_sort_order(cls, order: SortOrder) -> None:
        """Saves the sort order to settings."""
        cls.get_settings().setValue(SORT_ORDER_KEY, order.value)
        logger.debug(f"Sort order set to: {order.value}")
