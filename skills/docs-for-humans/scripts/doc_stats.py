#!/usr/bin/env python3
"""Count what the rewrite must report, and check relative links. Works for any language.

For each file prints: line count, bold count, broken relative links.
Bold is counted outside fenced code blocks and inline code.
A relative link is broken when its target file does not exist (anchors are ignored).

With --baseline ORIGINAL, also prints the bold ratio against the original
and fails when the rewrite keeps more than a quarter of the original's bold.

Exit code: 0 when all checks pass, 1 on any broken link or a failed bold ratio.

Usage: python3 doc_stats.py [--baseline ORIGINAL] <file>...
"""
import os
import re
import sys

BOLD_LIMIT = 0.25
SKIP_SCHEMES = ('http://', 'https://', 'mailto:', 'tel:', '#', '//')


def _prose_lines(text):
    """Yield (line_number, line) outside fenced code, with inline code removed."""
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, re.sub(r'`[^`]*`', '', line)


def count_bold(text):
    return sum(len(re.findall(r'\*\*[^*\n]+\*\*', line)) for _, line in _prose_lines(text))


def broken_links(text, base_dir):
    bad = []
    for n, line in _prose_lines(text):
        for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)', line):
            if target.startswith(SKIP_SCHEMES):
                continue
            path = target.split('#', 1)[0]
            if path and not os.path.exists(os.path.join(base_dir, path)):
                bad.append((n, target))
    return bad


def stats(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    return {
        'lines': len(text.splitlines()),
        'bold': count_bold(text),
        'broken': broken_links(text, os.path.dirname(os.path.abspath(path))),
    }


def main(argv):
    baseline = None
    if len(argv) >= 2 and argv[0] == '--baseline':
        baseline, argv = argv[1], argv[2:]
    if not argv:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2

    failed = False
    base = stats(baseline) if baseline else None
    if base:
        print(f'=== baseline {baseline}: {base["lines"]} lines, {base["bold"]} bold ===')
    for p in argv:
        s = stats(p)
        print(f'=== {p}: {s["lines"]} lines, {s["bold"]} bold, {len(s["broken"])} broken link(s) ===')
        for n, target in s['broken']:
            print(f'  {n}: broken link → {target}')
        failed |= bool(s['broken'])
        if base:
            limit = base['bold'] * BOLD_LIMIT
            ok = s['bold'] <= limit
            print(f'  bold {base["bold"]} → {s["bold"]} (limit {limit:g}): {"ok" if ok else "TOO MANY"}')
            print(f'  lines {base["lines"]} → {s["lines"]}')
            failed |= not ok
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
