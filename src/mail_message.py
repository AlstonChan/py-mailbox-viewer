from typing import Callable, Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging # Import logging for internal use

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
        headers: Dict[str, str],
        size: int,
        # Renamed body_parser to _body_content_provider and changed its return type
        _body_content_provider: Callable[[], Tuple[Optional[str], Optional[str], Optional[str]]],
        # Optional metadata that might be extracted or passed for convenience
        subject: Optional[str] = None,
        sender: Optional[str] = None, # From parsed 'From' header
        recipients: Optional[List[str]] = None, # From parsed 'To', 'Cc', 'Bcc' headers
        date_header: Optional[datetime] = None, # Parsed 'Date' header
        received_date: Optional[datetime] = None, # Parsed from a 'Received' header
        message_id: Optional[str] = None,
        source_identifier: Optional[Any] = None, # Unique ID/path for the original source
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
        """
        self.headers = headers
        self.size = size
        self._body_content_provider = _body_content_provider # Store the callable

        # Initialize caches for body content
        self._cached_raw_body: Optional[str] = None
        self._cached_plain_body: Optional[str] = None
        self._cached_html_body: Optional[str] = None
        self._body_content_loaded: bool = False # Flag to track if content has been loaded

        # Pre-extracted common fields for convenience
        self.subject = subject
        self.sender = sender
        self.recipients = recipients if recipients is not None else []
        self.date_header = date_header
        self.received_date = received_date
        self.message_id = message_id
        self.source_identifier = source_identifier

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
                logging.debug(f"Body content loaded for {self.message_id or self.source_identifier}")
            except Exception as e:
                logging.error(
                    f"Failed to load body content for message {self.message_id or self.source_identifier}: {e}",
                    exc_info=True
                )
                # Ensure caches are explicitly None on failure
                self._cached_raw_body = None
                self._cached_plain_body = None
                self._cached_html_body = None
            finally:
                self._body_content_loaded = True # Mark as loaded even if failed, to prevent repeated attempts


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

    def get_body(self) -> str:
        """
        Retrieves the plain text body content of the email.
        This method is kept for backward compatibility.
        For raw or HTML body, use .raw_body or .html_body properties.
        """
        self._load_body_content()
        return self._cached_plain_body or "" # Return empty string if plain body is None

    # --- Convenience properties for direct access to common raw headers ---
    @property
    def date(self) -> Optional[str]:
        """Returns the raw 'Date' header value."""
        return self.headers.get("Date")

    @property
    def from_(self) -> Optional[str]:
        """Returns the raw 'From' header value."""
        return self.headers.get("From")

    @property
    def to(self) -> Optional[str]:
        """Returns the raw 'To' header value."""
        return self.headers.get("To")

    @property
    def cc(self) -> Optional[str]:
        """Returns the raw 'Cc' header value."""
        return self.headers.get("Cc")

    @property
    def bcc(self) -> Optional[str]:
        """Returns the raw 'Bcc' header value (less common in received mail)."""
        return self.headers.get("Bcc")

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
        return self.headers.get("Received")

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
