"""Checks on the published package itself: examples pass the skill's own checks,
the manifest is valid, and every path SKILL.md names exists."""
import json
import re
import subprocess
import sys

import pytest

from conftest import EXAMPLES, ROOT, SCRIPTS, SKILL


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True)


@pytest.mark.parametrize('lang', ['en', 'zh-TW'])
def test_example_rewrite_passes_doc_stats(lang):
    d = EXAMPLES / lang
    r = run('doc_stats.py', '--baseline', d / 'before.md', d / 'after.md')
    assert r.returncode == 0, r.stdout


def test_zh_tw_example_passes_punctuation_check():
    assert run('check_punct.py', EXAMPLES / 'zh-TW' / 'after.md').returncode == 0


def test_zh_tw_example_original_fails_punctuation_check():
    assert run('check_punct.py', EXAMPLES / 'zh-TW' / 'before.md').returncode == 1


def test_zh_tw_module_passes_its_own_rule():
    assert run('check_punct.py', SKILL / 'lang' / 'zh-TW.md').returncode == 0


def test_plugin_manifest():
    m = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    assert m['name'] == 'mtouyang-skills'
    assert './skills/docs-for-humans' in m['skills']
    assert re.fullmatch(r'\d+\.\d+\.\d+', m['version'])


def test_skill_paths_exist():
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    paths =set(re.findall(r'\$\{CLAUDE_SKILL_DIR\}/([\w./-]+)', text))
    for mod in (SKILL / 'lang').glob('*.md'):
        paths |= set(re.findall(r'\$\{CLAUDE_SKILL_DIR\}/([\w./-]+)', mod.read_text(encoding='utf-8')))
    assert paths, 'SKILL.md should reference its files through ${CLAUDE_SKILL_DIR}'
    for p in paths:
        assert (SKILL / p).exists(), p


def test_skill_frontmatter_name_matches_directory():
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    m = re.search(r'^name:\s*(\S+)', text, re.M)
    assert m and m.group(1) == SKILL.name
