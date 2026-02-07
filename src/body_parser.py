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

from typing import Callable, Optional, Tuple
from email.message import Message
import mailbox
from logger_config import logger


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

    try:
        # Get raw body
        raw_body = msg.as_string()

        # Iterate through message parts to find plain text and HTML
        for part in msg.walk():
            # Skip the multipart container itself and explicit attachments
            if part.get_content_maintype() == "multipart" or (
                part.get("Content-Disposition")
                and part.get("Content-Disposition").startswith("attachment")
            ):
                continue

            content_type = part.get_content_type()
            charset = (
                part.get_content_charset() or "utf-8"
            )  # Default to utf-8 if charset not specified

            payload = part.get_payload(decode=True)
            if payload is None:
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


# TODO: Add other body parser factory functions here (e.g., for EML, custom formats)
