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

import logging
import os
import logging.handlers
from PySide6.QtCore import QStandardPaths, QCoreApplication
from constants import APP_NAME


_logger_instance = None  # Global logger instance


def setup_logging():
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance

    data_location = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
    log_dir = os.path.join(data_location, APP_NAME, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "app.log")

    _logger_instance = logging.getLogger(APP_NAME)
    _logger_instance.setLevel(logging.DEBUG)

    if _logger_instance.hasHandlers():
        _logger_instance.handlers.clear()

    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file_path, when="midnight", interval=1, backupCount=31, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    _logger_instance.addHandler(file_handler)

    if os.environ.get("APP_ENV", "development").lower() != "production":
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        _logger_instance.addHandler(console_handler)

    _logger_instance.info(f"Logging to file: {log_file_path}")

    return _logger_instance


def set_log_level(level: int):
    """
    Sets the logging level for the main logger and all its handlers.

    Args:
        level (int): The logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING).
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = (
            setup_logging()
        )  # Ensure logger is initialized if not already

    if not isinstance(level, int):
        _logger_instance.warning(
            f"Invalid log level type: {type(level)}. Expected an integer. Keeping current level."
        )
        return

    _logger_instance.setLevel(level)
    for handler in _logger_instance.handlers:
        handler.setLevel(level)
    _logger_instance.info(f"Log level set to: {logging.getLevelName(level)}")


# Initialize logger when module is imported and make it accessible
_logger_instance = setup_logging()
logger = _logger_instance
