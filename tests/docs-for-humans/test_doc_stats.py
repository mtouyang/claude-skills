import subprocess
import sys

from conftest import SCRIPTS
from doc_stats import broken_links, count_bold


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / 'doc_stats.py'), *map(str, args)],
                          capture_output=True, text=True)


def test_counts_bold_outside_code():
    text = '**a** and **b**\n`**not this**`\n```\n**nor this**\n```\n'
    assert count_bold(text) == 2


def test_broken_relative_link(tmp_path):
    (tmp_path / 'exists.md').write_text('x')
    text = ('[ok](exists.md) [anchor](exists.md#part) [web](https://example.com) '
            '[self](#top) [bad](missing.md)\n')
    assert broken_links(text, str(tmp_path)) == [(1, 'missing.md')]


def test_exit_code_1_on_broken_link(tmp_path):
    f = tmp_path / 'doc.md'
    f.write_text('[bad](missing.md)', encoding='utf-8')
    assert run(f).returncode == 1


def test_baseline_bold_ratio(tmp_path):
    original = tmp_path / 'before.md'
    original.write_text('**a** **b** **c** **d** **e** **f** **g** **h**', encoding='utf-8')
    ok, too_many = tmp_path / 'ok.md', tmp_path / 'too_many.md'
    ok.write_text('**a** **b**', encoding='utf-8')
    too_many.write_text('**a** **b** **c**', encoding='utf-8')
    assert run('--baseline', original, ok).returncode == 0
    r = run('--baseline', original, too_many)
    assert r.returncode == 1
    assert 'TOO MANY' in r.stdout
