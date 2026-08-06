import pytest

from teletext_hyphenate.wrap import TextTooLongError, is_c0_control, wrap_text


class FakeHyphenator:
    def __init__(self, points=None):
        self.points = points or {}

    def hyphenation_points(self, word):
        return self.points.get(word, [])


def test_wraps_with_space_in_first_column_before_controls():
    result = wrap_text("hei maailma", width=8, max_rows=5, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" hei", " maailma"]
    assert all(len(row) <= 8 for row in result.splitlines())


def test_uses_hyphenation_point_when_word_does_not_fit():
    result = wrap_text(
        "talonpoikainen",
        width=8,
        max_rows=5,
        hyphenator=FakeHyphenator({"talonpoikainen": [2, 5, 9]}),
    )

    assert result.splitlines() == [" talon-", " poikai-", " nen"]


def test_hard_splits_when_no_hyphenation_point_fits():
    result = wrap_text("abcdefgh", width=5, max_rows=5, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" abc-", " def-", " gh"]


def test_preserves_controls_and_carries_latest_control_to_next_rows():
    red = "\x01"
    green = "\x02"

    result = wrap_text(f"aa{red}bb cc{green}dd ee", width=6, max_rows=10, hyphenator=FakeHyphenator())

    assert result.splitlines() == [f" aa{red}bb", f"{red}cc{green}dd", f"{green}ee"]


def test_control_at_full_row_moves_to_next_row_and_then_carries():
    red = "\x01"

    result = wrap_text(f"abcd{red}ef", width=5, max_rows=5, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" abcd", f" {red}ef"]


def test_forced_newline_flushes_current_row():
    result = wrap_text("eka\ntoka", width=10, max_rows=5, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" eka", " toka"]


def test_max_rows_exceeded_raises_with_truncated_output():
    with pytest.raises(TextTooLongError) as exc_info:
        wrap_text("yksi kaksi kolme", width=7, max_rows=2, hyphenator=FakeHyphenator())

    assert exc_info.value.output == " yksi\n kaksi"


def test_c0_controls_exclude_newline_only():
    assert is_c0_control("\x01")
    assert is_c0_control("\t")
    assert not is_c0_control("\n")
    assert not is_c0_control(" ")
