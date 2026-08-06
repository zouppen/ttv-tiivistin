from teletext_hyphenate import cli
from teletext_hyphenate.voikko import VoikkoUnavailableError


class FakeHyphenator:
    def hyphenation_points(self, word):
        return []


def test_cli_success(monkeypatch, capsys):
    monkeypatch.setattr(cli.VoikkoHyphenator, "create", lambda: FakeHyphenator())
    monkeypatch.setattr(cli.sys.stdin, "read", lambda: "hei")

    assert cli.main(["--width", "10", "--max-rows", "2"]) == 0

    captured = capsys.readouterr()
    assert captured.out == " hei\n"
    assert captured.err == ""


def test_cli_too_long_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(cli.VoikkoHyphenator, "create", lambda: FakeHyphenator())
    monkeypatch.setattr(cli.sys.stdin, "read", lambda: "aa bb cc")

    assert cli.main(["--width", "5", "--max-rows", "1"]) == cli.EXIT_TOO_LONG

    captured = capsys.readouterr()
    assert captured.out == " aa\n"


def test_cli_voikko_unavailable_exit_code(monkeypatch, capsys):
    def raise_unavailable():
        raise VoikkoUnavailableError("missing")

    monkeypatch.setattr(cli.VoikkoHyphenator, "create", raise_unavailable)

    assert cli.main(["--width", "10", "--max-rows", "2"]) == cli.EXIT_VOIKKO_UNAVAILABLE

    captured = capsys.readouterr()
    assert "missing" in captured.err
