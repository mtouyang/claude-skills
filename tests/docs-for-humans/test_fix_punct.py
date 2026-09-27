import subprocess
import sys

from conftest import SCRIPTS
from fix_punct import convert


def test_converts_punctuation_next_to_chinese():
    assert convert('先確認空間,再執行備份;完成後驗證.') == '先確認空間，再執行備份；完成後驗證.'
    assert convert('注意:這一步很慢') == '注意：這一步很慢'
    assert convert('真的嗎?當然!') == '真的嗎？當然！'


def test_parentheses_become_full_width_only_around_chinese():
    assert convert('備份(約 40 GB)很大') == '備份（約 40 GB）很大'
    assert convert('run it (twice) now') == 'run it (twice) now'


def test_protects_code_urls_links_and_times():
    text = (
        '```\n中文,在 code block 裡,不動\n```\n'
        '行內 `a,b;c` 不動\n'
        '網址 https://example.com/a,b 不動\n'
        '見[說明](docs/a,b.md)\n'
        '排程在 03:30 跑\n'
    )
    out = convert(text)
    assert '中文,在 code block 裡,不動' in out
    assert '`a,b;c`' in out
    assert 'https://example.com/a,b' in out
    assert '](docs/a,b.md)' in out
    assert '03:30' in out


def test_leaves_english_untouched():
    text = 'Stop the service, then run: pg_restore (4 jobs). Done? Yes!'
    assert convert(text) == text


def test_idempotent():
    once = convert('先確認空間,再執行(約 40 GB).')
    assert convert(once) == once


def test_rewrites_file_in_place(tmp_path):
    f = tmp_path / 'doc.md'
    f.write_text('先備份,再遷移', encoding='utf-8')
    r = subprocess.run([sys.executable, str(SCRIPTS / 'fix_punct.py'), str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert f.read_text(encoding='utf-8') == '先備份，再遷移'
