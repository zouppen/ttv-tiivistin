import pytest

from teletext_hyphenate.teletext import TeletextEncodingError, encode_ep1_rows


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
