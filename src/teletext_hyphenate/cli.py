from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .teletext import EP1_GREEN, EP1_WHITE, EP1_WIDTH, TeletextEncodingError, build_ep1_page
from .voikko import VoikkoHyphenator, VoikkoUnavailableError
from .wrap import wrap_rows

EXIT_UNEXPECTED = 1
EXIT_USAGE = 2
EXIT_VOIKKO_UNAVAILABLE = 3
EXIT_TELETEXT_ENCODING = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teletext-hyphenate",
        description="Hyphenate and wrap Finnish text for teletext-style monospace rows.",
    )
    parser.add_argument("--width", type=_positive_int, help="total row width including column 1; text output only")
    parser.add_argument(
        "--format",
        choices=("text", "ep1"),
        default="text",
        help="output format; text uses UTF-8 rows, ep1 uses fixed-width teletext bytes",
    )
    parser.add_argument("-i", "--input", type=Path, help="input file path; defaults to standard input")
    parser.add_argument("-o", "--output", type=Path, help="output file path; defaults to standard output")
    parser.add_argument("-v", "--verbose", action="store_true", help="report output row count to standard error")
    parser.add_argument("--page-header", default="", help="right-justified EP1 page header text")
    parser.add_argument("--page-name", default="", help="left-justified EP1 page name text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.format == "ep1" and args.width is not None:
        parser.error("--width cannot be used with --format ep1; EP1 width is always 40")
    if args.format == "text" and args.width is None:
        parser.error("--width is required for text output")
    if args.width is not None and args.width < 2:
        parser.error("--width must be at least 2")

    try:
        hyphenator = VoikkoHyphenator.create()
        text = _read_input(args.input)
        if args.format == "ep1":
            output, row_count = _build_ep1_output(text, hyphenator, args.page_header, args.page_name)
            _write_binary_output(args.output, output)
        else:
            rows = wrap_rows(text, args.width, hyphenator)
            row_count = len(rows)
            _write_text_output(args.output, "\n".join(rows))
    except VoikkoUnavailableError as exc:
        print(f"teletext-hyphenate: {exc}", file=sys.stderr)
        return EXIT_VOIKKO_UNAVAILABLE
    except TeletextEncodingError as exc:
        print(f"teletext-hyphenate: {exc}", file=sys.stderr)
        return EXIT_TELETEXT_ENCODING
    except Exception as exc:
        print(f"teletext-hyphenate: unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED

    if args.verbose:
        print(f"teletext-hyphenate: rows={row_count}", file=sys.stderr)
    return 0


def _read_input(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


def _write_text_output(path: Path | None, output: str) -> None:
    text = output + "\n" if output else ""
    if path is None:
        sys.stdout.write(text)
        return
    path.write_text(text, encoding="utf-8")


def _write_binary_output(path: Path | None, output: bytes) -> None:
    if path is None:
        sys.stdout.buffer.write(output)
        return
    path.write_bytes(output)


def _build_ep1_output(text: str, hyphenator, page_header: str, page_name: str) -> tuple[bytes, int]:
    title, body = _split_ep1_input(text)
    title_rows = wrap_rows(EP1_GREEN + title + "\n", EP1_WIDTH, hyphenator)
    body_rows = wrap_rows(EP1_WHITE + body, EP1_WIDTH, hyphenator)
    return build_ep1_page(
        title_rows=title_rows,
        body_rows=body_rows,
        page_header=page_header,
        page_name=page_name,
    )


def _split_ep1_input(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines:
        return "", ""
    title = lines[0]
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "":
            return title, "\n".join(lines[index + 1 :])
    return title, ""


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
