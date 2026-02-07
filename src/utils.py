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

from typing import Optional, Union
import email.utils
from datetime import datetime
from logger_config import (
    logger,
)
from typing import Optional
from PySide6.QtWidgets import QLayout, QWidget, QLayoutItem


def parse_email_date(date_string: str) -> Optional[datetime]:
    """Parses an email date string into a datetime object."""
    try:
        return email.utils.parsedate_to_datetime(date_string)
    except (TypeError, ValueError):
        logger.warning(f"Could not parse date string: {date_string}")
        return None


def clear_layout(layout: Optional[QLayout]) -> None:
    if layout is None:
        return

    while layout.count():
        item = layout.takeAt(0)

        if item is None:
            continue

        widget: Optional[QWidget] = item.widget()
        if widget is not None:
            widget.deleteLater()
            continue

        child_layout: Optional[QLayout] = item.layout()
        if child_layout is not None:
            clear_layout(child_layout)
            child_layout.deleteLater()
            continue

        spacer = item.spacerItem()
        if spacer is not None:
            # nothing special needed, just let Qt GC it
            pass


def format_bytes(size: Union[int, float], precision: int = 2) -> str:
    if size < 0:
        raise ValueError("size must be non-negative")

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    value = float(size)

    for unit in units:
        if value < 1024.0:
            return f"{value:.{precision}f} {unit}"
        value /= 1024.0

    return f"{value:.{precision}f} EB"
