"""Synthetic tests for header validation regression.

These tests verify that HTTP headers containing trailing newline characters
are correctly rejected by the requests library's header validation logic.
Headers with embedded or trailing newlines could enable HTTP header injection
attacks and must always be rejected.
"""

import pytest

import requests
from requests.exceptions import InvalidHeader


class TestHeaderNewlineRejection:
    """Verify that header names and values ending with a bare newline
    are rejected.  RFC 7230 forbids \\n in both header names and values."""

    def test_header_value_trailing_newline_is_rejected(self):
        """A header value that ends with a bare LF must be caught by
        requests' own validation *before* reaching the HTTP layer."""
        with pytest.raises(InvalidHeader):
            requests.Request(
                "GET",
                "http://example.com",
                headers={"foo": "bar\n"},
            ).prepare()

    def test_header_value_single_newline_is_rejected(self):
        """A header value consisting of a single LF character must be
        rejected as invalid."""
        with pytest.raises(InvalidHeader):
            requests.Request(
                "GET",
                "http://example.com",
                headers={"foo": "\n"},
            ).prepare()

    def test_header_name_trailing_newline_is_rejected(self):
        """A header name ending with a bare LF must be rejected by
        the validation regex."""
        with pytest.raises(InvalidHeader):
            requests.Request(
                "GET",
                "http://example.com",
                headers={"foo\n": "bar"},
            ).prepare()

    def test_header_value_crlf_still_rejected(self):
        """Ensure CRLF in header values is still rejected (sanity check)."""
        with pytest.raises(InvalidHeader):
            requests.Request(
                "GET",
                "http://example.com",
                headers={"foo": "bar\r\n"},
            ).prepare()

    def test_valid_header_value_still_accepted(self):
        """Normal header values must still be accepted."""
        req = requests.Request(
            "GET",
            "http://example.com",
            headers={"foo": "bar baz qux"},
        ).prepare()
        assert req.headers["foo"] == "bar baz qux"

    def test_empty_header_value_still_accepted(self):
        """An empty header value must still be allowed."""
        req = requests.Request(
            "GET",
            "http://example.com",
            headers={"foo": ""},
        ).prepare()
        assert req.headers["foo"] == ""

    def test_regex_anchoring_value(self):
        """The header value regex must use end-of-string anchoring that
        does not treat a trailing \\n as an acceptable end-of-string.
        This is the core correctness requirement: the regex must reject
        any string that ends with \\n, even without preceding \\r."""
        from requests._internal_utils import _VALID_HEADER_VALUE_RE_STR

        # A trailing LF must NOT match
        assert _VALID_HEADER_VALUE_RE_STR.match("bar\n") is None
        # A single LF must NOT match
        assert _VALID_HEADER_VALUE_RE_STR.match("\n") is None
        # Normal values must still match
        assert _VALID_HEADER_VALUE_RE_STR.match("bar") is not None
        assert _VALID_HEADER_VALUE_RE_STR.match("") is not None

    def test_regex_anchoring_name(self):
        """The header name regex must use end-of-string anchoring that
        does not treat a trailing \\n as an acceptable end-of-string."""
        from requests._internal_utils import _VALID_HEADER_NAME_RE_STR

        # A trailing LF must NOT match
        assert _VALID_HEADER_NAME_RE_STR.match("foo\n") is None
        # Normal names must still match
        assert _VALID_HEADER_NAME_RE_STR.match("foo") is not None
