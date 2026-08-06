from teletext_hyphenate.voikko import VoikkoHyphenator


class PatternVoikko:
    def getHyphenationPattern(self, word):
        assert word == "abcde"
        return "  - ="


def test_hyphenation_points_from_voikko_pattern():
    hyphenator = VoikkoHyphenator(PatternVoikko())

    assert hyphenator.hyphenation_points("abcde") == [2, 4]
