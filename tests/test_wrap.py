from teletext_hyphenate.wrap import is_c0_control, wrap_rows, wrap_text


class FakeHyphenator:
    def __init__(self, points=None):
        self.points = points or {}

    def hyphenation_points(self, word):
        return self.points.get(word, [])


def test_wraps_with_space_in_first_column_before_controls():
    result = wrap_text("hei maailma", width=8, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" hei", " maailma"]
    assert all(len(row) <= 8 for row in result.splitlines())


def test_wrap_rows_returns_rows_without_joining():
    result = wrap_rows("hei maailma", width=8, hyphenator=FakeHyphenator())

    assert result == [" hei", " maailma"]


def test_uses_hyphenation_point_when_word_does_not_fit():
    result = wrap_text(
        "talonpoikainen",
        width=8,
        hyphenator=FakeHyphenator({"talonpoikainen": [2, 5, 9]}),
    )

    assert result.splitlines() == [" talon-", " poikai-", " nen"]


def test_hyphenates_word_onto_partially_filled_row():
    result = wrap_text(
        "alku talonpoikainen",
        width=14,
        hyphenator=FakeHyphenator({"talonpoikainen": [2, 5, 9]}),
    )

    assert result.splitlines() == [" alku talon-", " poikainen"]


def test_moves_word_when_no_hyphenation_point_fits_current_row():
    result = wrap_text(
        "alku talonpoikainen",
        width=10,
        hyphenator=FakeHyphenator({"talonpoikainen": [9]}),
    )

    assert result.splitlines() == [" alku", " talonpoi-", " kainen"]


def test_hard_splits_when_no_hyphenation_point_fits():
    result = wrap_text("abcdefgh", width=5, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" abc-", " def-", " gh"]


def test_preserves_controls_and_carries_latest_control_to_next_rows():
    red = "\x01"
    green = "\x02"

    result = wrap_text(f"aa{red}bb cc{green}dd ee", width=6, hyphenator=FakeHyphenator())

    assert result.splitlines() == [f" aa{red}bb", f"{red}cc{green}dd", f"{green}ee"]


def test_adjacent_controls_collapse_to_latter_control():
    blue = "\x04"
    white = "\x07"

    result = wrap_text(f"{blue}{white}teksti", width=10, hyphenator=FakeHyphenator())

    assert result.splitlines() == [f" {white}teksti"]


def test_carried_control_followed_by_control_collapses_to_latter_control():
    blue = "\x04"
    white = "\x07"

    result = wrap_text(f"pitkasana{blue}{white}jatko", width=10, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" pitkasana", f" {white}jatko"]


def test_controls_separated_by_text_are_preserved():
    blue = "\x04"
    white = "\x07"

    result = wrap_text(f"{blue}tai{white}radio", width=20, hyphenator=FakeHyphenator())

    assert result.splitlines() == [f" {blue}tai{white}radio"]


def test_control_at_full_row_moves_to_next_row_and_then_carries():
    red = "\x01"

    result = wrap_text(f"abcd{red}ef", width=5, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" abcd", f" {red}ef"]


def test_forced_newline_flushes_current_row():
    result = wrap_text("eka\ntoka", width=10, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" eka", " toka"]


def test_forced_blank_line_preserves_first_column_space():
    result = wrap_text("eka\n\ntoka", width=10, hyphenator=FakeHyphenator())

    assert result.splitlines() == [" eka", " ", " toka"]


def test_forced_blank_line_preserves_first_column_control():
    red = "\x01"

    result = wrap_text(f"eka{red}\n\ntoka", width=10, hyphenator=FakeHyphenator())

    assert result.splitlines() == [f" eka{red}", red, f"{red}toka"]


def test_c0_controls_exclude_newline_only():
    assert is_c0_control("\x01")
    assert is_c0_control("\t")
    assert not is_c0_control("\n")
    assert not is_c0_control(" ")
