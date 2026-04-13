"""
requests._internal_utils
~~~~~~~~~~~~~~

Provides utility functions that are consumed internally by Requests
which depend on extremely few external helpers (such as compat)
"""

import re

from .compat import builtin_str

# RFC 7230 Section 3.2.6 defines token characters for header field names:
#   token = 1*tchar
#   tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+"
#         / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
_RFC7230_TOKEN_CHARS = r"!#$%&'*+\-.^_`|~0-9A-Za-z"

# Header name validation: strictly RFC 7230 token characters only.
# This rejects non-token characters (e.g., control chars, spaces, colons)
# that were previously loosely accepted.
_VALID_HEADER_NAME_RE_BYTE = re.compile(
    rb"^[" + _RFC7230_TOKEN_CHARS.encode("ascii") + rb"]+\Z"
)
_VALID_HEADER_NAME_RE_STR = re.compile(
    r"^[" + _RFC7230_TOKEN_CHARS + r"]+\Z"
)

# Header value validation: reject ASCII control characters (0x00-0x08,
# 0x0A-0x1F, 0x7F) which can be used for header injection attacks.
# The first character must also be a visible (non-whitespace) character.
# Tab (0x09) is permitted within the value per RFC 7230 obs-text.
_VALID_HEADER_VALUE_RE_BYTE = re.compile(
    rb"^[^\x00-\x20\x7f][^\x00-\x08\x0a-\x1f\x7f]*\Z|^\Z"
)
_VALID_HEADER_VALUE_RE_STR = re.compile(
    r"^[^\x00-\x20\x7f][^\x00-\x08\x0a-\x1f\x7f]*\Z|^\Z"
)

_HEADER_VALIDATORS_STR = (_VALID_HEADER_NAME_RE_STR, _VALID_HEADER_VALUE_RE_STR)
_HEADER_VALIDATORS_BYTE = (_VALID_HEADER_NAME_RE_BYTE, _VALID_HEADER_VALUE_RE_BYTE)
HEADER_VALIDATORS = {
    bytes: _HEADER_VALIDATORS_BYTE,
    str: _HEADER_VALIDATORS_STR,
}


def to_native_string(string, encoding="ascii"):
    """Given a string object, regardless of type, returns a representation of
    that string in the native string type, encoding and decoding where
    necessary. This assumes ASCII unless told otherwise.
    """
    if isinstance(string, builtin_str):
        out = string
    else:
        out = string.decode(encoding)

    return out


def unicode_is_ascii(u_string):
    """Determine if unicode string only contains ASCII characters.

    :param str u_string: unicode string to check. Must be unicode
        and not Python 2 `str`.
    :rtype: bool
    """
    assert isinstance(u_string, str)
    try:
        u_string.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False
