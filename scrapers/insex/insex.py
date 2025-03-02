"""
No-op scene scraper for Insex-based sites.

This is purely useful to enabe per-site search capabilities.

The original Insex scraper must be used after populating the
scene URL via search and this no-op scraper.
"""

import json
import sys

fragment = json.loads(sys.stdin.read())

# No-op but remove details.
# Details are only used as placeholder for the search result screen.
fragment.pop("details")

print(json.dumps(fragment))
