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
EP1 output has no newline separators; every row is padded with spaces to exactly
`--width` bytes.

```sh
teletext-hyphenate --width 40 --format ep1 --input input.txt --output output.ep1
```

Rows reserve their first column for the latest C0 control character seen in the
input, or a regular space before any control character has been seen. C0 control
characters are preserved in the output and treated as whitespace for
hyphenation.

EP1 output uses the Teletext Latin G0 Swedish/Finnish/Hungarian national
character subset. Input is still UTF-8.

Exit codes:

- `0`: success
- `1`: unexpected runtime error
- `2`: command-line usage error
- `3`: Voikko is unavailable or no Finnish dictionary can be opened
- `4`: text cannot be encoded in the selected teletext output character set
