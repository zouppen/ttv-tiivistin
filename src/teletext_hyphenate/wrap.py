from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Hyphenator(Protocol):
    def hyphenation_points(self, word: str) -> list[int]:
        """Return positions where the word may be split with an inserted hyphen."""


@dataclass
class Wrapper:
    width: int
    hyphenator: Hyphenator

    def __post_init__(self) -> None:
        if self.width < 2:
            raise ValueError("width must be at least 2")
        self._rows: list[str] = []
        self._carry = " "
        self._line = self._carry

    @property
    def _content_width(self) -> int:
        return self.width - 1

    @property
    def _remaining(self) -> int:
        return self.width - len(self._line)

    def wrap(self, text: str) -> str:
        for token in _tokenize(text):
            kind, value = token.kind, token.value
            if kind == "newline":
                self._flush()
            elif kind == "control":
                self._add_control(value)
            elif kind == "space":
                self._add_space()
            else:
                self._add_word(value)
        self._flush()
        return "\n".join(self._rows)

    def _flush(self) -> None:
        self._rows.append(self._line.rstrip(" ") or self._carry)
        self._line = self._carry

    def _ensure_room(self, cells: int = 1) -> None:
        if self._remaining < cells:
            self._flush()

    def _add_control(self, char: str) -> None:
        self._ensure_room()
        self._line += char
        self._carry = char

    def _add_space(self) -> None:
        if len(self._line) == 1:
            return
        self._ensure_room()
        if len(self._line) > 1 and not self._line.endswith(" "):
            self._line += " "

    def _add_word(self, word: str) -> None:
        while word:
            if len(word) <= self._remaining:
                self._line += word
                return

            if self._remaining < 2:
                self._flush()
                continue

            split_at = self._best_hyphenation_point(word, self._remaining)
            if split_at is None and len(self._line) > 1:
                self._flush()
                continue

            if split_at is None:
                split_at = self._remaining - 1

            self._line += word[:split_at] + "-"
            word = word[split_at:]
            self._flush()

    def _best_hyphenation_point(self, word: str, available: int) -> int | None:
        max_prefix = available - 1
        candidates = [point for point in self.hyphenator.hyphenation_points(word) if point <= max_prefix]
        if not candidates:
            return None
        return max(candidates)


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


def wrap_text(text: str, width: int, hyphenator: Hyphenator) -> str:
    return Wrapper(width=width, hyphenator=hyphenator).wrap(text)


def is_c0_control(char: str) -> bool:
    return ord(char) < 32 and char != "\n"


def _tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    current: list[str] = []

    def flush_word() -> None:
        if current:
            tokens.append(Token("word", "".join(current)))
            current.clear()

    for char in text:
        if char == "\n":
            flush_word()
            tokens.append(Token("newline", char))
        elif is_c0_control(char):
            flush_word()
            tokens.append(Token("control", char))
        elif char.isspace():
            flush_word()
            tokens.append(Token("space", char))
        else:
            current.append(char)
    flush_word()
    return tokens
