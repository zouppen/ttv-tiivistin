from __future__ import annotations


class TeletextEncodingError(ValueError):
    """Raised when text cannot be represented in the target teletext charset."""


NATIONAL_CHARS = {
    "#": 0x23,
    "¤": 0x24,
    "É": 0x40,
    "Ä": 0x5B,
    "Ö": 0x5C,
    "Å": 0x5D,
    "Ü": 0x5E,
    "_": 0x5F,
    "é": 0x60,
    "ä": 0x7B,
    "ö": 0x7C,
    "å": 0x7D,
    "ü": 0x7E,
}

DIRECT_PRINTABLES = {
    *(chr(code) for code in range(0x20, 0x23)),
    *(chr(code) for code in range(0x25, 0x40)),
    *(chr(code) for code in range(0x41, 0x5B)),
    *(chr(code) for code in range(0x61, 0x7B)),
}


def encode_ep1_rows(rows: list[str], width: int) -> bytes:
    encoded = bytearray()
    for row_number, row in enumerate(rows, start=1):
        if len(row) > width:
            raise TeletextEncodingError(f"row {row_number} exceeds width {width}")
        padded = row.ljust(width, " ")
        for column, char in enumerate(padded, start=1):
            encoded.append(_encode_char(char, row_number, column))
    return bytes(encoded)


def _encode_char(char: str, row_number: int, column: int) -> int:
    codepoint = ord(char)
    if codepoint < 0x20:
        return codepoint
    if char in NATIONAL_CHARS:
        return NATIONAL_CHARS[char]
    if char in DIRECT_PRINTABLES:
        return codepoint
    raise TeletextEncodingError(
        f"character {char!r} at row {row_number}, column {column} is not supported by the teletext charset"
    )
