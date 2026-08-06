from pathlib import Path

import pytest

from teletext_hyphenate.teletext import (
    EP1_FOOTER,
    EP1_HEADER,
    EP1_PAGE_HEADER_MAX_LENGTH,
    EP1_PAGE_NAME_MAX_LENGTH,
    EP1_PAGE_NAME_PREFIX,
    EP1_PAGE_SIZE,
    EP1_WIDTH,
    TeletextEncodingError,
    build_ep1_page,
    encode_ep1_rows,
)


def test_encode_ep1_rows_pads_to_fixed_width_without_newlines():
    assert encode_ep1_rows([" abc", " de"], width=5) == b" abc  de  "


def test_encode_ep1_rows_preserves_c0_controls():
    assert encode_ep1_rows([" \x01A"], width=4) == b" \x01A "


def test_encode_ep1_rows_uses_swedish_finnish_hungarian_charset():
    rows = [" #¤ÉÄÖÅÜ_éäöåü"]

    assert encode_ep1_rows(rows, width=len(rows[0])) == bytes(
        [0x20, 0x23, 0x24, 0x40, 0x5B, 0x5C, 0x5D, 0x5E, 0x5F, 0x60, 0x7B, 0x7C, 0x7D, 0x7E]
    )


def test_encode_ep1_rows_rejects_unsupported_character():
    with pytest.raises(TeletextEncodingError, match="not supported"):
        encode_ep1_rows([" €"], width=2)


def test_encode_ep1_rows_rejects_too_wide_row():
    with pytest.raises(TeletextEncodingError, match="exceeds width"):
        encode_ep1_rows([" abc"], width=3)


def test_build_ep1_page_adds_header_layout_and_fixed_size():
    output, rows = build_ep1_page(
        title_rows=[" \x02Otsikko", "\x02"],
        body_rows=[" \x07Leipäteksti"],
        page_header="10/23",
        page_name="Radioamatööriliiton tiedote 6.8.2026",
    )

    assert len(output) == EP1_PAGE_SIZE
    assert output[-2:] == EP1_FOOTER
    assert rows == 3
    assert output.startswith(EP1_HEADER)
    page_rows = _page_rows(output)
    assert page_rows[0] == b" " * EP1_WIDTH
    assert page_rows[1] == b" " * 35 + b"10/23"
    assert page_rows[2].startswith(b"\x04\x1d\x07Radioamat")
    assert page_rows[3] == b" " * EP1_WIDTH
    assert page_rows[4].startswith(b"\x02O")
    assert b"\x07Leip{" in output


def test_target_fixture_has_expected_page_shape():
    fixture = Path("examples/tavoite.ep1").read_bytes()

    assert len(fixture) == EP1_PAGE_SIZE
    assert fixture.startswith(EP1_HEADER)
    assert fixture[-2:] == EP1_FOOTER
    page_rows = _page_rows(fixture)
    assert len(page_rows) == 25
    assert page_rows[0] == b" " * EP1_WIDTH
    assert page_rows[1] == b" " * 35 + b"10/23"
    assert page_rows[2].startswith(b"\x04\x1d\x07Radioamat")
    assert page_rows[4].startswith(b"\x02")
    assert page_rows[6].startswith(b"\x07")


def test_build_ep1_page_accepts_max_length_metadata():
    output, _ = build_ep1_page(
        title_rows=[],
        body_rows=[],
        page_header="H" * EP1_PAGE_HEADER_MAX_LENGTH,
        page_name="N" * EP1_PAGE_NAME_MAX_LENGTH,
    )

    page_rows = _page_rows(output)
    assert page_rows[1] == b"H" * EP1_PAGE_HEADER_MAX_LENGTH
    assert page_rows[2] == EP1_PAGE_NAME_PREFIX.encode("ascii") + (b"N" * EP1_PAGE_NAME_MAX_LENGTH)


def test_build_ep1_page_rejects_too_long_page_header():
    with pytest.raises(TeletextEncodingError, match="--page-header"):
        build_ep1_page(title_rows=[], body_rows=[], page_header="H" * 41, page_name="")


def test_build_ep1_page_rejects_too_long_page_name():
    with pytest.raises(TeletextEncodingError, match="--page-name"):
        build_ep1_page(title_rows=[], body_rows=[], page_header="", page_name="N" * 38)


def _page_rows(output: bytes) -> list[bytes]:
    page = output[len(EP1_HEADER) : -len(EP1_FOOTER)]
    return [page[index : index + EP1_WIDTH] for index in range(0, len(page), EP1_WIDTH)]
