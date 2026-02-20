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
import email
import email.parser
import email.policy
import email.message
import email.utils
from email.header import decode_header, make_header
from typing import List, Optional, Tuple

from PySide6.QtCore import QObject, Signal

from logger_config import logger
from mail_message import MailMessage
from body_parser import create_file_body_content_provider
from utils import parse_email_date

# Byte prefix that marks the start of a new message in mbox format
_MBOX_FROM_PREFIX = b"From "


def _parse_headers_only(header_bytes: bytes) -> email.message.Message:
    """Parse raw header bytes into an email.message.Message (headers only)."""
    parser = email.parser.BytesParser(policy=email.policy.compat32)
    return parser.parsebytes(header_bytes)


def _scan_mbox_offsets(file_path: str) -> List[Tuple[int, int]]:
    """Scan the mbox file and return a list of (msg_start, msg_length) tuples.

    msg_start is the byte offset of the first header line (after the 'From '
    separator).  msg_length is the number of bytes from msg_start to the end
    of the message (just before the next 'From ' line or EOF).

    This does a single sequential read of the file with minimal memory usage.
    """
    offsets: List[Tuple[int, int]] = []
    current_msg_start: Optional[int] = None

    with open(file_path, "rb") as f:
        while True:
            line_start = f.tell()
            line = f.readline()
            if not line:
                # EOF – close out the last message
                if current_msg_start is not None:
                    offsets.append((current_msg_start, line_start - current_msg_start))
                break

            if line.startswith(_MBOX_FROM_PREFIX):
                # Close out previous message
                if current_msg_start is not None:
                    offsets.append((current_msg_start, line_start - current_msg_start))
                # New message starts on the next line (after the "From " line)
                current_msg_start = f.tell()

    return offsets


def _read_header_block(file_path: str, msg_start: int, msg_length: int) -> bytes:
    """Read only the header portion of a message (up to the first blank line)."""
    # Read a reasonable chunk – headers are rarely > 16 KB, but cap at msg_length
    read_size = min(msg_length, 64 * 1024)
    with open(file_path, "rb") as f:
        f.seek(msg_start)
        chunk = f.read(read_size)

    # Headers end at the first blank line (\r\n\r\n or \n\n)
    sep = b"\r\n\r\n"
    idx = chunk.find(sep)
    if idx == -1:
        sep = b"\n\n"
        idx = chunk.find(sep)
    if idx != -1:
        return chunk[: idx + len(sep)]
    # No blank line found in the chunk – return everything we read (edge case)
    return chunk


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
            # --- Phase 1: single sequential scan to find message offsets ---
            offsets = _scan_mbox_offsets(self.file_path)

            if not offsets:
                # File may not be mbox – apply the same fallback logic as before
                # Try reading first bytes to see if it's genuinely empty vs wrong format
                with open(self.file_path, "rb") as f:
                    head = f.read(64)
                if head and not head.startswith(_MBOX_FROM_PREFIX):
                    raise ValueError("Not a valid mbox file")
                # Truly empty or valid mbox with zero messages
                self.finished.emit(emails, self.file_path)
                return

            logger.debug(f"Scanned {len(offsets)} message(s) in {self.file_path}.")

            # --- Phase 2: read only headers for each message ---
            for index, (msg_start, msg_length) in enumerate(offsets):
                try:
                    header_bytes = _read_header_block(
                        self.file_path, msg_start, msg_length
                    )
                    message = _parse_headers_only(header_bytes)

                    headers = defaultdict(list)
                    for k, v in message.items():
                        headers[k].append(str(v))
                    headers = dict(headers)

                    # Use the raw byte length as size (avoids re-serialisation)
                    size = msg_length

                    raw_subject = message.get("Subject")
                    try:
                        subject = (
                            str(make_header(decode_header(raw_subject)))
                            if raw_subject
                            else None
                        )
                        if subject:
                            # Collapse folded whitespace (\n, \r\n followed by
                            # whitespace) left over from RFC 5322 header folding
                            subject = " ".join(subject.splitlines()).strip()
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
                        _body_content_provider=create_file_body_content_provider(
                            self.file_path, msg_start, msg_length
                        ),
                        subject=subject,
                        sender=sender,
                        recipients=recipients,
                        date_header=date_header,
                        message_id=message.get("Message-ID"),
                        source_identifier=f"{self.file_path}:{index}",
                    )
                    emails.append(mail_msg)
                except Exception as e:
                    logger.warning(
                        f"Skipping message at offset {msg_start}: {e}",
                        exc_info=True,
                    )

            self.finished.emit(emails, self.file_path)
        except ValueError:
            logger.debug(
                f"File {self.file_path} is not a valid MBOX file by content. "
                "Checking for other formats."
            )
            if self.file_path.endswith(".eml"):
                self.error.emit("info", "EML file parsing is not yet implemented.")
            else:
                self.error.emit(
                    "unsupported",
                    f"The file '{self.file_path}' is not a recognized mail "
                    "format (mbox, eml).",
                )
        except Exception as e:
            logger.error(f"Error loading file {self.file_path}: {e}", exc_info=True)
            self.error.emit(
                "critical",
                f"Failed to load file '{self.file_path}': {e}\n"
                "Check logs for details.",
            )
