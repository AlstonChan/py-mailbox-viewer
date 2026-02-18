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

from collections import defaultdict
import mailbox
import email.utils
from email.header import decode_header, make_header
from typing import List

from PySide6.QtCore import QObject, Signal

from logger_config import logger
from mail_message import MailMessage
from body_parser import create_mbox_body_content_provider
from utils import parse_email_date


class EmailLoaderWorker(QObject):
    """Worker that loads emails from a mail file in a background thread.

    Signals:
        finished: Emitted with the loaded emails and the file path on success.
        error: Emitted with an error type and message on failure.
            Error types: "info", "unsupported", "critical".
    """

    finished = Signal(list, str)  # (emails, file_path)
    error = Signal(str, str)  # (error_type, error_message)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self) -> None:
        emails: List[MailMessage] = []
        try:
            mbox = mailbox.mbox(self.file_path)
            logger.debug(f"Attempting to load {self.file_path} as MBOX.")
            for key, message in mbox.items():
                headers = defaultdict(list)
                for k, v in message.items():
                    headers[k].append(str(v))
                headers = dict(headers)

                size = len(message.as_bytes())

                raw_subject = message.get("Subject")
                try:
                    subject = (
                        str(make_header(decode_header(raw_subject)))
                        if raw_subject
                        else None
                    )
                except Exception:
                    subject = raw_subject

                sender = message.get("From")

                recipients: List[str] = []
                for header_name in ["To", "Cc", "Bcc"]:
                    addresses = email.utils.getaddresses(
                        message.get_all(header_name, [])
                    )
                    recipients.extend([addr for name, addr in addresses if addr])

                date_header_str = message.get("Date")
                date_header = (
                    parse_email_date(date_header_str) if date_header_str else None
                )

                mail_msg = MailMessage(
                    headers=headers,
                    size=size,
                    _body_content_provider=create_mbox_body_content_provider(mbox, key),
                    subject=subject,
                    sender=sender,
                    recipients=recipients,
                    date_header=date_header,
                    message_id=message.get("Message-ID"),
                    source_identifier=f"{self.file_path}:{key}",
                )
                emails.append(mail_msg)
            self.finished.emit(emails, self.file_path)
        except mailbox.FormatError:
            logger.debug(
                f"File {self.file_path} is not a valid MBOX file by content. Checking for other formats."
            )
            if self.file_path.endswith(".eml"):
                self.error.emit("info", "EML file parsing is not yet implemented.")
            else:
                self.error.emit(
                    "unsupported",
                    f"The file '{self.file_path}' is not a recognized mail format (mbox, eml).",
                )
        except Exception as e:
            logger.error(f"Error loading file {self.file_path}: {e}", exc_info=True)
            self.error.emit(
                "critical",
                f"Failed to load file '{self.file_path}': {e}\nCheck logs for details.",
            )
