from __future__ import annotations


class TeletextEncodingError(ValueError):
    """Raised when text cannot be represented in the target teletext charset."""


EP1_WIDTH = 40
EP1_PAGE_SIZE = 1008
EP1_HEADER = b"\xfe\x01\x18\x00\x00\x00  "
EP1_HEADER_TRAILER = "\x04\x1d"
EP1_GREEN = "\x02"
EP1_WHITE = "\x07"
EP1_COLORED_SECTION_GUTTER = 38

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


def build_ep1_page(
    *,
    title_rows: list[str],
    body_rows: list[str],
    page_header: str,
    page_name: str,
) -> tuple[bytes, int]:
    rows = [
        " " * EP1_WIDTH,
        (page_header + EP1_HEADER_TRAILER).rjust(EP1_WIDTH),
        EP1_WHITE + page_name,
    ]
    colored_rows = [_strip_initial_carry(row) for row in title_rows + body_rows]
    unpadded = (
        EP1_HEADER
        + encode_ep1_rows(rows, EP1_WIDTH)
        + (b" " * EP1_COLORED_SECTION_GUTTER)
        + encode_ep1_rows(colored_rows, EP1_WIDTH)
    )
    return _fit_ep1_page(unpadded), len(rows) + len(colored_rows)


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


def _fit_ep1_page(data: bytes) -> bytes:
    if len(data) >= EP1_PAGE_SIZE:
        return data[:EP1_PAGE_SIZE]
    padded = bytearray(data + (b" " * (EP1_PAGE_SIZE - len(data))))
    padded[-2:] = b"\x00\x00"
    return bytes(padded)


def _strip_initial_carry(row: str) -> str:
    if row.startswith(" "):
        return row[1:]
    return row
