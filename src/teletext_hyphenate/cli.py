from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .voikko import VoikkoHyphenator, VoikkoUnavailableError
from .wrap import wrap_text

EXIT_UNEXPECTED = 1
EXIT_USAGE = 2
EXIT_VOIKKO_UNAVAILABLE = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teletext-hyphenate",
        description="Hyphenate and wrap Finnish text for teletext-style monospace rows.",
    )
    parser.add_argument("--width", type=_positive_int, required=True, help="total row width including column 1")
    parser.add_argument("-i", "--input", type=Path, help="input file path; defaults to standard input")
    parser.add_argument("-o", "--output", type=Path, help="output file path; defaults to standard output")
    parser.add_argument("-v", "--verbose", action="store_true", help="report output row count to standard error")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.width < 2:
        parser.error("--width must be at least 2")

    try:
        hyphenator = VoikkoHyphenator.create()
        text = _read_input(args.input)
        output = wrap_text(text, args.width, hyphenator)
        _write_output(args.output, output)
    except VoikkoUnavailableError as exc:
        print(f"teletext-hyphenate: {exc}", file=sys.stderr)
        return EXIT_VOIKKO_UNAVAILABLE
    except Exception as exc:
        print(f"teletext-hyphenate: unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED

    if args.verbose:
        print(f"teletext-hyphenate: rows={_row_count(output)}", file=sys.stderr)
    return 0


def _read_input(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


def _write_output(path: Path | None, output: str) -> None:
    text = output + "\n" if output else ""
    if path is None:
        sys.stdout.write(text)
        return
    path.write_text(text, encoding="utf-8")


def _row_count(output: str) -> int:
    if output == "":
        return 0
    return len(output.split("\n"))


def _positive_int(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
