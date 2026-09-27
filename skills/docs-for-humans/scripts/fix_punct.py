#!/usr/bin/env python3
"""Convert half-width punctuation in Chinese text to full-width, in place (zh-TW docs).

Protects fenced code blocks, inline code, Markdown link targets, URLs, and times.
Idempotent: running it twice changes nothing the second time.
Always verify afterwards with check_punct.py and read the diff yourself.

Usage: python3 fix_punct.py <file>...
"""
import re
import sys

HAN = '一-鿿'


def convert(text):
    held = []

    def hide(m):
        held.append(m.group(0))
        return f'\x00{len(held) - 1}\x00'

    # Protect: fences, inline code, link targets, URLs, times.
    text = re.sub(r'```.*?```', hide, text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', hide, text)
    text = re.sub(r'\]\([^)\n]*\)', hide, text)
    text = re.sub(r'https?://\S+', hide, text)
    text = re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\b', hide, text)

    # Comma, semicolon: convert when either side is Chinese, and eat one following space.
    for half, full in ((',', '，'), (';', '；')):
        text = re.sub(rf'(?<=[{HAN}]){re.escape(half)} ?', full, text)
        text = re.sub(rf'{re.escape(half)} ?(?=[{HAN}])', full, text)
    # Colon, question mark, exclamation mark: convert when preceded by Chinese.
    text = re.sub(rf'(?<=[{HAN}]): ?', '：', text)
    text = re.sub(rf'(?<=[{HAN}])\? ?', '？', text)
    text = re.sub(rf'(?<=[{HAN}])! ?', '！', text)

    # Parentheses: full-width only when the content contains Chinese.
    def paren(m):
        inner = m.group(1)
        if re.search(f'[{HAN}、。，；：？！「」（）]', inner.replace('\x00', '')):
            return f'（{inner}）'
        return m.group(0)
    text = re.sub(r'\(([^()\n]*)\)', paren, text)

    # Restore held text (may nest, so repeat until stable).
    for _ in range(5):
        new = re.sub(r'\x00(\d+)\x00', lambda m: held[int(m.group(1))], text)
        if new == text:
            break
        text = new
    return text


def main(paths):
    for p in paths:
        with open(p, encoding='utf-8') as f:
            s = f.read()
        out = convert(s)
        if out != s:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(out)
            print(f'rewritten {p}')
        else:
            print(f'unchanged {p}')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    sys.exit(main(sys.argv[1:]))
