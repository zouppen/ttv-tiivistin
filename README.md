# teletext-hyphenate

Finnish teletext-aware text wrapping for monospace output.

The command reads UTF-8 text from standard input and writes wrapped text to
standard output:

```sh
teletext-hyphenate --width 40 --max-rows 10 < input.txt > output.txt
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
- `4`: output was truncated because `--max-rows` was exceeded
