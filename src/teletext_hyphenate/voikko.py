from __future__ import annotations

from dataclasses import dataclass


class VoikkoUnavailableError(RuntimeError):
    """Raised when Voikko or its Finnish dictionary cannot be initialized."""


@dataclass
class VoikkoHyphenator:
    voikko: object

    @classmethod
    def create(cls) -> "VoikkoHyphenator":
        try:
            from libvoikko import Voikko
        except Exception as exc:  # pragma: no cover - depends on host package
            raise VoikkoUnavailableError("Python package libvoikko is not available") from exc

        try:
            dictionaries = Voikko.listDicts()
        except Exception as exc:  # pragma: no cover - depends on host native library
            raise VoikkoUnavailableError("native libvoikko library is not available") from exc

        if not any(dictionary.language == "fi" for dictionary in dictionaries):
            raise VoikkoUnavailableError("Voikko Finnish dictionary could not be opened")

        try:
            voikko = Voikko("fi")
        except Exception as exc:  # pragma: no cover - depends on host dictionaries
            raise VoikkoUnavailableError("Voikko Finnish dictionary could not be opened") from exc

        return cls(voikko)

    def hyphenation_points(self, word: str) -> list[int]:
        """Return split positions where inserting '-' before word[index] is allowed."""
        pattern = self.voikko.getHyphenationPattern(word)
        points: list[int] = []
        for index, marker in enumerate(pattern):
            if marker in "-=" and 0 < index < len(word):
                points.append(index)
        return points
