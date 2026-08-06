from teletext_hyphenate import cli
from teletext_hyphenate.voikko import VoikkoUnavailableError


class FakeHyphenator:
    def hyphenation_points(self, word):
        return []


def test_cli_success(monkeypatch, capsys):
    monkeypatch.setattr(cli.VoikkoHyphenator, "create", lambda: FakeHyphenator())
    monkeypatch.setattr(cli.sys.stdin, "read", lambda: "hei")

    assert cli.main(["--width", "10"]) == 0

    captured = capsys.readouterr()
    assert captured.out == " hei\n"
    assert captured.err == ""


def test_cli_verbose_reports_row_count(monkeypatch, capsys):
    monkeypatch.setattr(cli.VoikkoHyphenator, "create", lambda: FakeHyphenator())
    monkeypatch.setattr(cli.sys.stdin, "read", lambda: "aa bb cc")

    assert cli.main(["--width", "5", "--verbose"]) == 0

    captured = capsys.readouterr()
    assert captured.out == " aa\n bb\n cc\n"
    assert captured.err == "teletext-hyphenate: rows=3\n"


def test_cli_reads_and_writes_files(monkeypatch, tmp_path, capsys):
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.txt"
    input_path.write_text("hei maailma", encoding="utf-8")
    monkeypatch.setattr(cli.VoikkoHyphenator, "create", lambda: FakeHyphenator())

    assert cli.main(["--width", "8", "--input", str(input_path), "--output", str(output_path)]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert output_path.read_text(encoding="utf-8") == " hei\n maailma\n"


def test_cli_voikko_unavailable_exit_code(monkeypatch, capsys):
    def raise_unavailable():
        raise VoikkoUnavailableError("missing")

    monkeypatch.setattr(cli.VoikkoHyphenator, "create", raise_unavailable)

    assert cli.main(["--width", "10"]) == cli.EXIT_VOIKKO_UNAVAILABLE

    captured = capsys.readouterr()
    assert "missing" in captured.err


def test_cli_invalid_width_uses_argparse_exit_code():
    try:
        cli.main(["--width", "1"])
    except SystemExit as exc:
        assert exc.code == cli.EXIT_USAGE
    else:
        raise AssertionError("expected argparse to exit")
