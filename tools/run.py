#!/usr/bin/env python3
"""Run the whole PDF -> site pipeline.

    python3 tools/run.py            # full run
    python3 tools/run.py --fast     # reuse cached text/figure extraction

Requires: pip install -r tools/requirements.txt
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def step(name, script):
    print(f'\n▶ {name}')
    r = subprocess.run([sys.executable, os.path.join(HERE, script)], cwd=HERE)
    if r.returncode:
        sys.exit(f'✗ {script} failed')


def main():
    import paths  # noqa: F401  (validates the PDF path / creates the cache dir)
    if not os.path.exists(paths.PDF):
        sys.exit(f'✗ PDF not found at {paths.PDF}')

    fast = '--fast' in sys.argv
    have_cache = os.path.exists(paths.LINES_JSON) and os.path.exists(paths.CHARTS_JSON)

    if not (fast and have_cache):
        step('Extracting text lines + geometry', 'lines.py')
        step('Rendering chart figures', 'charts.py')
    else:
        print('▶ Reusing cached extraction (--fast)')

    step('Building MDX chapters, glossary and figures', 'build.py')
    print('\n✓ Done. Now run:  cd site && npm install && npm run dev')


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    main()
