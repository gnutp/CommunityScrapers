"""
A generic sitemap scraper.

Allows to search for a scene or performer by name, matching
on the locations listed in the sitemap of a website.
"""

import json
import sys

sys.path.append("./community")

import py_common.log as log
from py_common.cache import cache_to_disk
from py_common.util import scraper_args

from py_common.types import SceneSearchResult, PerformerSearchResult

from lxml import etree

from urllib.parse import urlparse

from pathlib import Path

import difflib


@cache_to_disk(key="sitemap", ttl=360)
def parse_sitemap(base_url: str) -> list:
    url = urlparse(base_url)
    sitemap = Path(f"{url.hostname}.xml")

    with sitemap.open() as f:
        content = f.read_text()

    root = etree.fromstring(content)
    namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = root.xpath("//ns:loc/text()", namespaces=namespaces)

    return urls


def normalise(text: str) -> str:
    translation_map = str.maketrans({"-": " "})
    return text.translate(translation_map).lower()


def matches_by_name(name: str, site_url: str, filter: str = ""):
    """
    Matches a location in the sitemap by name.

    :param name: The name to match for in the location titles.
    :param site_url: The site URL for which to fetch the sitemap.
    :param filter: Additional filtering to perform in the locations, defaults to "" (no filter)
    :return: Up to 10 best matches.
    """
    urls = parse_sitemap(site_url)

    input = normalise(name)
    candidates = [urlparse(u).path for u in urls if filter in u]
    matches = difflib.get_close_matches(input, candidates, 10, 0.3)

    return matches


def scene_by_name(name: str, site_url: str, filter: str) -> list[SceneSearchResult]:
    matches = matches_by_name(name, site_url, filter)
    return [{"title": m.split("/")[-1], "url": f"{site_url}{m}"} for m in matches]


def performer_by_name(
    name: str, site_url: str, filter: str
) -> list[PerformerSearchResult]:
    matches = matches_by_name(name, site_url, filter)
    return [{"name": m.split("/")[-1], "url": f"{site_url}{m}"} for m in matches]


if __name__ == "__main__":
    op, args = scraper_args()

    result = None
    extra = args.get("extra", None)
    site_url = extra[0]
    (filter,) = extra[1:2] or ("",)

    match op, args:
        case "scene-by-name", {"name": name} if name:
            result = scene_by_name(name, site_url, filter)
        case "performer-by-name", {"name": name} if name:
            result = performer_by_name(name, site_url, filter)
        case _:
            log.error(
                f"Not implemented: Operation: {op}, arguments: {json.dumps(args)}"
            )
            sys.exit(1)

    log.debug("result: %s" % result)
    print(json.dumps(result))
