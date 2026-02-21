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

from typing import Callable, Any, List, Mapping, Optional, Tuple
from datetime import datetime
from logger_config import logger
import re
import email.utils

# Import at module level – body_parser is a sibling module
from body_parser import Attachment


class MailMessage:
    """
    Represents a single email message, abstracting its source.
    This class can hold all possible mail content like headers, size, date,
    received information, subject, etc. The body content is retrieved
    via a callable function to support different underlying storage mechanisms
    (e.g., mbox keys, EML file parsing) and provides access to raw, plain, and HTML formats.
    """

    def __init__(
        self,
        headers: Mapping[str, List[str]],
        size: int,
        _body_content_provider: Callable[
            [], Tuple[Optional[str], Optional[str], Optional[str]]
        ],
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        date_header: Optional[datetime] = None,
        received_date: Optional[datetime] = None,
        message_id: Optional[str] = None,
        source_identifier: Optional[
            Any
        ] = None,  # Unique ID/path for the original source
        _attachment_provider: Optional[Callable[[], List[Attachment]]] = None,
    ):
        """
        Initializes a MailMessage object.

        Args:
            headers (Dict[str, str]): A dictionary of mail headers (e.g., {"Subject": "Hello"}).
                                      Keys are header names (case-insensitive usually handled by parser).
            size (int): The size of the mail message in bytes.
            _body_content_provider (Callable[[], Tuple[Optional[str], Optional[str], Optional[str]]]):
                                            A callable (function) that, when invoked,
                                            returns a tuple containing (raw_body, plain_body, html_body).
            subject (Optional[str]): The subject of the email.
            sender (Optional[str]): The sender's email address or name.
            recipients (Optional[List[str]]): A list of recipient email addresses or names.
            date_header (Optional[datetime]): The parsed date from the 'Date' header.
            received_date (Optional[datetime]): A parsed date from a 'Received' header.
            message_id (Optional[str]): The Message-ID of the email.
            source_identifier (Optional[Any]): An identifier for the original source of the mail
                                            (e.g., file path, index in an mbox file).
            _attachment_provider (Optional[Callable[[], List[Attachment]]]): A callable (function) that, when invoked,
                                            returns a list of attachments.
        """
        self.headers = headers
        self.size = size
        self._body_content_provider = _body_content_provider  # Store the callable

        # Initialize caches for body content
        self._cached_raw_body: Optional[str] = None
        self._cached_plain_body: Optional[str] = None
        self._cached_html_body: Optional[str] = None
        self._body_content_loaded: bool = (
            False  # Flag to track if content has been loaded
        )

        # Pre-extracted common fields for convenience
        self.subject = subject
        self.sender = sender
        self.recipients = recipients if recipients is not None else []
        self.date_header = date_header
        self.received_date = received_date
        self.message_id = message_id
        self.source_identifier = source_identifier

        # Attachment provider (lazy)
        self._attachment_provider = _attachment_provider
        self._cached_attachments: Optional[List[Attachment]] = None
        self._attachments_loaded: bool = False

    def _load_body_content(self) -> None:
        """
        Internal method to load body content from the provider and cache it.
        Ensures content is loaded only once.
        """
        if not self._body_content_loaded:
            try:
                raw, plain, html = self._body_content_provider()
                self._cached_raw_body = raw
                self._cached_plain_body = plain
                self._cached_html_body = html
                logger.debug(
                    f"CACHE MISS, Body content loaded for {self.message_id or self.source_identifier}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to load body content for message {self.message_id or self.source_identifier}: {e}",
                    exc_info=True,
                )
                # Ensure caches are explicitly None on failure
                self._cached_raw_body = None
                self._cached_plain_body = None
                self._cached_html_body = None
            finally:
                self._body_content_loaded = (
                    True  # Mark as loaded even if failed, to prevent repeated attempts
                )
        else:
            logger.debug(
                f"CACHE HIT, Body content retrieved from cache for {self.message_id or self.source_identifier}"
            )

    @property
    def raw_body(self) -> Optional[str]:
        """Returns the raw body content of the email."""
        self._load_body_content()
        return self._cached_raw_body

    @property
    def plain_body(self) -> Optional[str]:
        """Returns the plain text body content of the email."""
        self._load_body_content()
        return self._cached_plain_body

    @property
    def html_body(self) -> Optional[str]:
        """Returns the HTML body content of the email."""
        self._load_body_content()
        return self._cached_html_body

    @property
    def attachments(self) -> List[Attachment]:
        """Returns the list of attachments for this email (lazy-loaded)."""
        if not self._attachments_loaded:
            if self._attachment_provider is not None:
                try:
                    self._cached_attachments = self._attachment_provider()
                    logger.debug(
                        f"Loaded {len(self._cached_attachments)} attachment(s) for "
                        f"{self.message_id or self.source_identifier}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to load attachments for {self.message_id or self.source_identifier}: {e}",
                        exc_info=True,
                    )
                    self._cached_attachments = []
            else:
                self._cached_attachments = []
            self._attachments_loaded = True
        return self._cached_attachments or []

    def get_body(self) -> str:
        """
        Retrieves the plain text body content of the email.
        This method is kept for backward compatibility.
        For raw or HTML body, use .raw_body or .html_body properties.
        """
        self._load_body_content()
        return (
            self._cached_plain_body or ""
        )  # Return empty string if plain body is None

    # --- Convenience properties for direct access to common raw headers ---
    def get_header(self, name: str) -> Optional[str]:
        values = self.headers.get(name)
        return values[0] if values else None

    def get_all_headers(self, name: str) -> List[str]:
        return self.headers.get(name, [])

    @property
    def date(self) -> Optional[str]:
        """Returns the raw 'Date' header value."""
        return self.get_header("Date")

    @property
    def from_(self) -> Optional[str]:
        """Returns the raw 'From' header value."""
        return self.get_header("From")

    @property
    def to(self) -> Optional[str]:
        """Returns the raw 'To' header value."""
        return self.get_header("To")

    @property
    def cc(self) -> Optional[str]:
        """Returns the raw 'Cc' header value."""
        return self.get_header("Cc")

    @property
    def bcc(self) -> Optional[str]:
        """Returns the raw 'Bcc' header value (less common in received mail)."""
        return self.get_header("Bcc")

    @property
    def reply_to(self) -> Optional[str]:
        """Returns the raw 'Reply-To' header value."""
        return self.get_header("Reply-To")

    @property
    def formatted_to_full(self) -> List[str]:
        """Returns a list of fully formatted 'To' email addresses (e.g., "Name <email>")."""
        return self._format_address_list(self.to, format_type="full")

    @property
    def formatted_to_names(self) -> List[str]:
        """Returns a list of 'To' email display names."""
        return self._format_address_list(self.to, format_type="name")

    @property
    def formatted_to_emails(self) -> List[str]:
        """Returns a list of 'To' email addresses (email part only)."""
        return self._format_address_list(self.to, format_type="email")

    @property
    def formatted_cc_full(self) -> List[str]:
        """Returns a list of fully formatted 'Cc' email addresses (e.g., "Name <email>")."""
        return self._format_address_list(self.cc, format_type="full")

    @property
    def formatted_cc_names(self) -> List[str]:
        """Returns a list of 'Cc' email display names."""
        return self._format_address_list(self.cc, format_type="name")

    @property
    def formatted_cc_emails(self) -> List[str]:
        """Returns a list of 'Cc' email addresses (email part only)."""
        return self._format_address_list(self.cc, format_type="email")

    @property
    def formatted_bcc_full(self) -> List[str]:
        """Returns a list of fully formatted 'Bcc' email addresses (e.g., "Name <email>")."""
        return self._format_address_list(self.bcc, format_type="full")

    @property
    def formatted_bcc_names(self) -> List[str]:
        """Returns a list of 'Bcc' email display names."""
        return self._format_address_list(self.bcc, format_type="name")

    @property
    def formatted_bcc_emails(self) -> List[str]:
        """Returns a list of 'Bcc' email addresses (email part only)."""
        return self._format_address_list(self.bcc, format_type="email")

    def _format_address_list(
        self, raw_addresses_string: Optional[str], format_type: str
    ) -> List[str]:
        """
        Helper method to parse and format a list of addresses from a raw header string.
        format_type can be 'full', 'name', or 'email'.
        """
        if not raw_addresses_string:
            return []

        formatted_list: List[str] = []
        for name, email_address in email.utils.getaddresses([raw_addresses_string]):
            cleaned_name = self._clean_name_part(name)
            cleaned_email = self._clean_email_part(email_address)

            if format_type == "full":
                if cleaned_name and cleaned_email:
                    formatted_list.append(f"{cleaned_name} <{cleaned_email}>")
                elif cleaned_email:
                    formatted_list.append(cleaned_email)
                elif cleaned_name:
                    formatted_list.append(cleaned_name)
            elif format_type == "name":
                if cleaned_name:
                    formatted_list.append(cleaned_name)
            elif format_type == "email":
                if cleaned_email:
                    formatted_list.append(cleaned_email)
        return formatted_list

    @property
    def formatted_from_full_address(self) -> Optional[str]:
        """Returns the fully formatted 'From' email address (e.g., "Name <email>")."""
        raw_from = self.from_
        if not raw_from:
            return None
        name, email_address = self._parse_address_components(raw_from)
        cleaned_name = self._clean_name_part(name)
        cleaned_email = self._clean_email_part(email_address)

        if cleaned_name and cleaned_email:
            return f"{cleaned_name} <{cleaned_email}>"
        elif cleaned_email:
            return cleaned_email
        elif cleaned_name:
            return cleaned_name
        return None

    @property
    def formatted_from_name(self) -> Optional[str]:
        """Returns the 'From' email display name."""
        raw_from = self.from_
        if not raw_from:
            return None
        name, _ = self._parse_address_components(raw_from)
        cleaned_name = self._clean_name_part(name)
        return cleaned_name if cleaned_name else None

    @property
    def formatted_from_email(self) -> Optional[str]:
        """Returns the 'From' email address (email part only)."""
        raw_from = self.from_
        if not raw_from:
            return None
        _, email_address = self._parse_address_components(raw_from)
        cleaned_email = self._clean_email_part(email_address)
        return cleaned_email if cleaned_email else None

    @property
    def formatted_message_id(self) -> Optional[str]:
        """Returns the Message-ID with angle brackets removed, if present."""
        if self.message_id:
            # Remove leading '<' and trailing '>' if they exist
            return self.message_id.strip("<>").strip()
        return None

    @property
    def mailed_by(self) -> Optional[str]:
        """
        Returns the SMTP server domain that handed the mail to the recipient server.
        Derived from Received, Return-Path, or From headers.
        """

        # 1. Try Received headers
        received_headers = self.get_all_headers("Received")
        if received_headers:
            # First Received header = closest server to recipient
            first = received_headers[0]

            # Extract "from <server>"
            match = re.search(r"from\s+([^\s\(\);]+)", first, re.IGNORECASE)
            if match:
                return match.group(1)

        # 2. Fallback to Return-Path
        return_path = self.get_header("Return-Path")
        if return_path:
            match = re.search(r"@([^>\s]+)", return_path)
            if match:
                return match.group(1)

        # 3. Fallback to From domain
        if self.from_:
            match = re.search(r"@([^>\s]+)", self.from_)
            if match:
                return match.group(1)

        return None

    @property
    def received_raw(self) -> Optional[str]:
        """
        Returns the raw 'Received' header value.
        Note: A mail can have multiple 'Received' headers. This property
        will typically return the value of the first or last 'Received'
        header, depending on how the `headers` dictionary was populated.
        More sophisticated parsing would be needed to access all 'Received'
        headers if multiple exist.
        """
        return self.get_header("Received")

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the MailMessage object.
        """
        return (
            f"MailMessage(Subject='{self.subject or 'N/A'}', "
            f"Sender='{self.sender or self.from_ or 'N/A'}', "
            f"Date='{self.date_header.isoformat() if self.date_header else self.date or 'N/A'}', "
            f"Size={self.size})"
        )

    @staticmethod
    def _parse_address_components(address_string: str) -> Tuple[str, str]:
        """
        Parses a single email address string into its name and email parts.
        Uses email.utils.parseaddr for robust parsing.
        Returns a tuple of (name, email).
        """
        if not address_string:
            return "", ""
        return email.utils.parseaddr(address_string)

    @staticmethod
    def _clean_name_part(name: str) -> str:
        """Removes quotes from a name string and strips whitespace."""
        return name.strip().strip('"')

    @staticmethod
    def _clean_email_part(email_address: str) -> str:
        """Removes angle brackets from an email address string and strips whitespace."""
        return email_address.strip()
