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

from typing import Callable, List, Optional, Tuple
import email
from email.message import Message
from email.header import decode_header, make_header
import mailbox
import os
from dataclasses import dataclass
from logger_config import logger


@dataclass
class Attachment:
    """Represents an email attachment."""

    filename: str
    content_type: str
    payload: bytes  # raw binary content


def _decode_filename(raw: Optional[str]) -> Optional[str]:
    """Decode an RFC 2047-encoded filename, if needed."""
    if raw is None:
        return None
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return raw


def _extract_attachments(msg: Message) -> List[Attachment]:
    """
    Extracts attachment parts from an email message.
    Returns a list of Attachment objects.
    """
    attachments: List[Attachment] = []
    try:
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue

            disposition = part.get_content_disposition()
            filename = _decode_filename(part.get_filename())

            # Consider a part an attachment if it has a Content-Disposition of
            # "attachment", or if it has a filename and is not inline text.
            is_attachment = disposition == "attachment"
            is_named_non_body = (
                filename
                and disposition != "inline"
                and part.get_content_type() not in ("text/plain", "text/html")
            )
            # Also treat inline non-text parts with a filename as attachments
            is_inline_binary = (
                filename
                and disposition == "inline"
                and part.get_content_maintype() not in ("text",)
            )

            if is_attachment or is_named_non_body or is_inline_binary:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                if not isinstance(payload, bytes):
                    continue
                name = filename or f"attachment_{len(attachments) + 1}"
                attachments.append(
                    Attachment(
                        filename=name,
                        content_type=part.get_content_type(),
                        payload=payload,
                    )
                )
    except Exception as e:
        logger.error(f"Error extracting attachments: {e}", exc_info=True)
    return attachments


def _extract_body_parts(
    msg: Message,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extracts raw, plain text, and HTML body content from an email.
    Returns a tuple: (raw_body, plain_body, html_body).
    """
    raw_body = None
    plain_body = None
    html_body = None

    logger.debug("Extracting body parts from email message.")

    try:
        # Get raw body
        raw_body = msg.as_string()

        # Iterate through message parts to find plain text and HTML
        for part in msg.walk():
            # Skip the multipart container itself and explicit attachments
            disposition = part.get_content_disposition()
            if part.get_content_maintype() == "multipart" or (
                disposition and disposition == "attachment"
            ):
                continue

            content_type = part.get_content_type()
            charset = (
                part.get_content_charset() or "utf-8"
            )  # Default to utf-8 if charset not specified

            payload = part.get_payload(decode=True)
            if payload is None:
                continue

            # Skip if payload is not bytes (e.g., Message objects in nested multipart)
            if not isinstance(payload, bytes):
                continue

            try:
                decoded_payload = payload.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                # Fallback for unknown or incorrect charsets
                decoded_payload = payload.decode("latin-1", errors="replace")

            if content_type == "text/plain" and plain_body is None:
                plain_body = decoded_payload
            elif content_type == "text/html" and html_body is None:
                html_body = decoded_payload

    except Exception as e:
        logger.error(f"Error extracting body parts: {e}", exc_info=True)

    return raw_body, plain_body, html_body


def create_mbox_body_content_provider(
    mbox_obj: mailbox.mbox, key: str
) -> Callable[[], Tuple[Optional[str], Optional[str], Optional[str]]]:
    """
    Returns a callable that, when invoked, retrieves an email message from an mbox
    object and extracts its raw, plain text, and HTML body content.
    This enables lazy loading of message bodies and provides content in multiple formats.

    Args:
        mbox_obj (mailbox.mbox): The mbox object containing the email message.
        key (Any): The key identifying the message within the mbox object.

    Returns:
        Callable[[], Tuple[Optional[str], Optional[str], Optional[str]]]: A callable
        that, when executed, returns a tuple containing (raw_body, plain_body, html_body).
        Returns (None, None, None) if an error occurs or message is not found.
    """

    def body_content_provider_func() -> (
        Tuple[Optional[str], Optional[str], Optional[str]]
    ):
        try:
            msg = mbox_obj.get_message(key)  # Retrieve the message only when needed
            if msg is None:
                logger.warning(f"Message with key '{key}' not found in mbox.")
                return None, None, None
            return _extract_body_parts(msg)
        except Exception as e:
            logger.error(
                f"Error retrieving or parsing mbox message with key '{key}': {e}",
                exc_info=True,
            )
            return None, None, None

    return body_content_provider_func


def create_file_body_content_provider(
    file_path: str, msg_start: int, msg_length: int
) -> Callable[[], Tuple[Optional[str], Optional[str], Optional[str]]]:
    """
    Returns a callable that, when invoked, reads the raw message bytes from the
    mbox file at the given offset and extracts body content.

    This avoids keeping the entire mbox object in memory and supports lazy
    loading of message bodies directly from disk.

    Args:
        file_path (str): Path to the mbox file.
        msg_start (int): Byte offset where the message starts (after the 'From ' line).
        msg_length (int): Number of bytes for this message.

    Returns:
        Callable that returns (raw_body, plain_body, html_body).
    """

    def body_content_provider_func() -> (
        Tuple[Optional[str], Optional[str], Optional[str]]
    ):
        try:
            with open(file_path, "rb") as f:
                f.seek(msg_start)
                raw_bytes = f.read(msg_length)
            msg = email.message_from_bytes(raw_bytes)
            return _extract_body_parts(msg)
        except Exception as e:
            logger.error(
                f"Error reading message at offset {msg_start} from '{file_path}': {e}",
                exc_info=True,
            )
            return None, None, None

    return body_content_provider_func


def create_file_attachment_provider(
    file_path: str, msg_start: int, msg_length: int
) -> Callable[[], List[Attachment]]:
    """
    Returns a callable that, when invoked, reads the raw message bytes from the
    mbox file at the given offset and extracts attachments.

    Args:
        file_path (str): Path to the mbox file.
        msg_start (int): Byte offset where the message starts.
        msg_length (int): Number of bytes for this message.

    Returns:
        Callable that returns a list of Attachment objects.
    """

    def attachment_provider_func() -> List[Attachment]:
        try:
            with open(file_path, "rb") as f:
                f.seek(msg_start)
                raw_bytes = f.read(msg_length)
            msg = email.message_from_bytes(raw_bytes)
            return _extract_attachments(msg)
        except Exception as e:
            logger.error(
                f"Error reading attachments at offset {msg_start} from '{file_path}': {e}",
                exc_info=True,
            )
            return []

    return attachment_provider_func


# TODO: Add other body parser factory functions here (e.g., for EML, custom formats)
