"""
No-op scraper for search operations.
"""

import json
import sys

fragment = json.loads(sys.stdin.read())

# no-op
print(json.dumps(fragment))
