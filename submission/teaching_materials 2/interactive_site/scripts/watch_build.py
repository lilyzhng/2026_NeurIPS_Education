#!/usr/bin/env python3
"""Rebuild index.html whenever sections/*.md or template.html changes.

  python3 watch_build.py     # Ctrl-C to stop
"""
import os, subprocess, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATCH = [os.path.join(HERE, 'template.html'), os.path.join(HERE, 'scripts', 'build.py')]


def snapshot():
    files = list(WATCH)
    secdir = os.path.join(HERE, 'sections')
    files += [os.path.join(secdir, f) for f in os.listdir(secdir) if f.endswith('.md')]
    return {f: os.path.getmtime(f) for f in files if os.path.exists(f)}


last = {}
print('watching sections/*.md + template.html; Ctrl-C to stop')
while True:
    cur = snapshot()
    if cur != last:
        if last:
            changed = [os.path.basename(f) for f in cur if cur.get(f) != last.get(f)]
            print(time.strftime('%H:%M:%S'), 'changed:', ', '.join(changed))
        subprocess.run(['python3', os.path.join(HERE, 'scripts', 'build.py')], cwd=HERE)
        last = cur
    time.sleep(1)
