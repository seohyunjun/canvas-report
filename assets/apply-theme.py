#!/usr/bin/env python3
"""Swap one theme from themes.css into a report's [T] block.

    python3 assets/apply-theme.py <report.html> <theme> [--themes assets/themes.css]
    python3 assets/apply-theme.py --list

Pasting by hand is easy to get wrong: miss a brace and the [T]/[/T] marks are
gone, and nothing can swap the theme again. This script only ever replaces the
text between the marks, so you can re-theme a report as often as you like.
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN_MARK = '/* [T] theme tokens'
CLOSE_MARK = '/* [/T] end theme tokens'


def themes_in(css):
    """themes.css -> {name: block text}"""
    parts = re.split(r'(?m)^/\* ── THEME ([A-Z]+) ', css)
    out = {}
    for i in range(1, len(parts), 2):
        out[parts[i].lower()] = '/* ── THEME ' + parts[i] + ' ' + parts[i + 1].rstrip() + '\n'
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('report', nargs='?', help='the report HTML to re-theme')
    ap.add_argument('theme', nargs='?', help='theme name, e.g. newsprint')
    ap.add_argument('--themes', default=os.path.join(HERE, 'themes.css'))
    ap.add_argument('--list', action='store_true', help='list available themes and exit')
    a = ap.parse_args()

    css = io.open(a.themes, encoding='utf-8').read()
    table = themes_in(css)

    if a.list:
        print('\n'.join(sorted(table)))
        return
    if not a.report or not a.theme:
        ap.error('give both a report path and a theme name (or --list)')

    name = a.theme.lower()
    if name not in table:
        sys.exit('no theme %r. Available: %s' % (a.theme, ', '.join(sorted(table))))

    html = io.open(a.report, encoding='utf-8').read()
    i = html.find(OPEN_MARK)
    j = html.find(CLOSE_MARK)
    if i < 0 or j < 0:
        sys.exit('could not find the [T] marks — the shell token block has been damaged.')

    head_end = html.index('*/', i) + 3          # keep the marker comment itself
    io.open(a.report, 'w', encoding='utf-8').write(html[:head_end] + table[name] + html[j:])
    print('%s -> %s' % (os.path.basename(a.report), name))


if __name__ == '__main__':
    main()
