from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .voikko import VoikkoHyphenator, VoikkoUnavailableError
from .wrap import TextTooLongError, wrap_text

EXIT_UNEXPECTED = 1
EXIT_USAGE = 2
EXIT_VOIKKO_UNAVAILABLE = 3
EXIT_TOO_LONG = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teletext-hyphenate",
        description="Hyphenate and wrap Finnish text for teletext-style monospace rows.",
    )
    parser.add_argument("--width", type=_positive_int, required=True, help="total row width including column 1")
    parser.add_argument("--max-rows", type=_positive_int, required=True, help="maximum number of output rows")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.width < 2:
        parser.error("--width must be at least 2")

    try:
        hyphenator = VoikkoHyphenator.create()
        output = wrap_text(sys.stdin.read(), args.width, args.max_rows, hyphenator)
    except VoikkoUnavailableError as exc:
        print(f"teletext-hyphenate: {exc}", file=sys.stderr)
        return EXIT_VOIKKO_UNAVAILABLE
    except TextTooLongError as exc:
        if exc.output:
            sys.stdout.write(exc.output)
            sys.stdout.write("\n")
        return EXIT_TOO_LONG
    except Exception as exc:
        print(f"teletext-hyphenate: unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED

    if output:
        sys.stdout.write(output)
        sys.stdout.write("\n")
    return 0


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
