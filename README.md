# teletext-hyphenate

Finnish teletext-aware text wrapping for monospace output.

The command reads UTF-8 text from standard input and writes wrapped text to
standard output by default:

```sh
teletext-hyphenate --width 40 < input.txt > output.txt
```

Input and output files can also be supplied explicitly:

```sh
teletext-hyphenate --width 40 --input input.txt --output output.txt
```

Use `--verbose` or `-v` to report the number of output rows to standard error.

```sh
teletext-hyphenate --width 40 --verbose < input.txt > output.txt
```

Rows reserve their first column for the latest C0 control character seen in the
input, or a regular space before any control character has been seen. C0 control
characters are preserved in the output and treated as whitespace for
hyphenation.

Exit codes:

- `0`: success
- `1`: unexpected runtime error
- `2`: command-line usage error
- `3`: Voikko is unavailable or no Finnish dictionary can be opened
