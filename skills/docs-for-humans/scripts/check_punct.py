#!/usr/bin/env python3
"""Find half-width punctuation next to Chinese characters (zh-TW docs).

Skips fenced code blocks, inline code, and Markdown link targets.
Exit code: 0 when every file is clean, 1 when any hit is found.

Usage: python3 check_punct.py <file>...
"""
import re
import sys

HAN = r'一-鿿'
# Half-width punctuation touching a Chinese character should be full-width.
RULES = [
    (r'[' + HAN + r'][,;!?]', 'half-width , ; ! ? after Chinese'),
    (r'[,;!?][' + HAN + r']', 'half-width , ; ! ? before Chinese'),
    (r'[' + HAN + r']\(', 'half-width ( after Chinese'),
    (r'\)[' + HAN + r']', 'half-width ) before Chinese'),
    (r'[' + HAN + r']:(?!//)', 'half-width : after Chinese'),
    (r'[' + HAN + r']\.(?=\s|$)', 'half-width full stop after Chinese'),
    (r'\([' + HAN + r']', 'half-width ( around Chinese'),
    (r'[' + HAN + r']\)', 'half-width ) around Chinese'),
]


def scan_text(text):
    """Return a list of (line_number, reason, context) hits."""
    hits, in_fence = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        clean = re.sub(r'`[^`]*`', '', line)
        clean = re.sub(r'\]\([^)]*\)', ']', clean)
        for pat, why in RULES:
            for m in re.finditer(pat, clean):
                ctx = clean[max(0, m.start() - 18):m.end() + 18].strip()
                hits.append((n, why, ctx))
    return hits


def main(paths):
    total = 0
    for p in paths:
        with open(p, encoding='utf-8') as f:
            hits = scan_text(f.read())
        total += len(hits)
        print(f'=== {p}: {len(hits)} hit(s) ===')
        for n, why, ctx in hits[:40]:
            print(f'  {n}: {why} … {ctx}')
        if len(hits) > 40:
            print(f'  … {len(hits) - 40} more')
    return 1 if total else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    sys.exit(main(sys.argv[1:]))
