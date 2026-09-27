import subprocess
import sys

from conftest import SCRIPTS
from check_punct import scan_text


def run(*paths):
    return subprocess.run([sys.executable, str(SCRIPTS / 'check_punct.py'), *map(str, paths)],
                          capture_output=True, text=True)


def test_finds_half_width_next_to_chinese():
    hits = scan_text('先備份,再遷移\n注意:很慢\n')
    assert [n for n, _, _ in hits] == [1, 1, 2]


def test_ignores_code_and_link_targets():
    text = '```\n中文,不算\n```\n行內 `中文,不算`\n見[說明](中文,不算.md)\n'
    assert scan_text(text) == []


def test_exit_code_1_when_hits(tmp_path):
    f = tmp_path / 'bad.md'
    f.write_text('先備份,再遷移', encoding='utf-8')
    assert run(f).returncode == 1


def test_exit_code_0_when_clean(tmp_path):
    f = tmp_path / 'good.md'
    f.write_text('先備份，再遷移', encoding='utf-8')
    assert run(f).returncode == 0


def test_any_dirty_file_fails_the_run(tmp_path):
    good, bad = tmp_path / 'good.md', tmp_path / 'bad.md'
    good.write_text('先備份，再遷移', encoding='utf-8')
    bad.write_text('先備份,再遷移', encoding='utf-8')
    assert run(good, bad).returncode == 1
