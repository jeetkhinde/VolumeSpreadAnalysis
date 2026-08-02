"""Shared paths for the extraction pipeline. All tools run from anywhere."""
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CACHE = os.path.join(TOOLS, '.cache')

PDF = os.path.join(ROOT, 'Master the Markets by Tom Williams.pdf')
LINES_JSON = os.path.join(CACHE, 'lines.json')
CHARTS_JSON = os.path.join(CACHE, 'charts.json')
FIGS_RAW = os.path.join(CACHE, 'figs')

SITE = os.path.join(ROOT, 'site')
CONTENT = os.path.join(SITE, 'src', 'content')
FIGS_OUT = os.path.join(SITE, 'public', 'figures')

os.makedirs(CACHE, exist_ok=True)
