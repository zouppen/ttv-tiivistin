# teletext-hyphenate

Finnish teletext-aware text wrapping for monospace output.

The command reads UTF-8 text from standard input and writes wrapped text to
standard output by default:

```sh
teletext-hyphenate --width 40 < input.txt > output.txt
```

Text output is the default format. It emits UTF-8 rows separated by newlines.

Input and output files can also be supplied explicitly:

```sh
teletext-hyphenate --width 40 --input input.txt --output output.txt
```

Use `--verbose` or `-v` to report the number of output rows to standard error.

```sh
teletext-hyphenate --width 40 --verbose < input.txt > output.txt
```

Use `--format ep1` to write fixed-width teletext bytes instead of UTF-8 text.
EP1 output has a 6-byte header, 25 rows of 40 bytes, and a 2-byte footer. There
are no newline separators.

```sh
teletext-hyphenate \
  --format ep1 \
  --page-header 10/23 \
  --page-name "Radioamatööriliiton tiedote 6.8.2026" \
  --input input.txt \
  --output output.ep1
```

In EP1 output, `--page-header` can be at most 40 characters and `--page-name`
can be at most 37 characters.

Rows reserve their first column for the latest C0 control character seen in the
input, or a regular space before any control character has been seen. C0 control
characters are preserved in the output and treated as whitespace for
hyphenation.

EP1 output always produces exactly 1008 bytes, padding or truncating the
generated page as needed. Do not pass `--width` with
`--format ep1`. EP1 output uses the Teletext Latin G0 Swedish/Finnish/Hungarian
national character subset. Input is still UTF-8.

Exit codes:

- `0`: success
- `1`: unexpected runtime error
- `2`: command-line usage error
- `3`: Voikko is unavailable or no Finnish dictionary can be opened
- `4`: text cannot be encoded in the selected teletext output character set

## Automatic summaries

See the [prompt.txt](prompt.txt), place the input file accordingly and run in a container:

```
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox - <prompt.txt
```

And enjoy this fully automated teletext page generator from any PDF input.
