"""
Script to enhance the 'gord.json' output from 'gord.js', making
it importable into stashdb.

Usage:
1. Run 'gord.js' to scrape all House of Gord model metadata.
2. Run 'gord.py' which will create a folder './performers/' that can be
   imported into StashDB. This will download the model images and
   convert them to base64 as required by the StashDB import format. [1]
3. ZIP the resulting folder and import via the Stash DB UI.

[1]: https://docs.stashapp.cc/in-app-manual/tasks/jsonspec/
"""

from urllib.request import Request, urlopen, urlparse, quote
import base64
import json
from time import sleep
from typing import TypedDict, Literal
from pathlib import Path
from datetime import datetime


class HouseOfGordModel(TypedDict):
    name: str
    image: str
    url: str


class Performer(TypedDict):
    name: str
    disambiguation: str
    gender: Literal["FEMALE", "MALE"]
    urls: list[str]
    aliases: list[str]
    image: str
    created_at: datetime
    updated_at: datetime


def make_safe_url(url: str) -> str:
    """
    Returns a parsed and quoted url
    """
    _url = urlparse(url)
    url = _url.scheme + "://" + _url.netloc + quote(_url.path)
    return url


input_file = Path("gord.json")
output_dir = Path("performers")

output_dir.mkdir(parents=True, exist_ok=True)

with open(input_file) as f:
    models: list[HouseOfGordModel] = json.load(f)

now = datetime.now().astimezone().replace(microsecond=0).isoformat()

for model in models:
    # Aliases are included in the model name, separated by '/', e.g.
    # 'Adrianna Nicole/ Seven/ Petal'.
    names = [x.strip() for x in model["name"].split("/")]
    name = names[0]
    aliases = names[1:]

    image_url = make_safe_url(model["image"])

    # print(f"Reading '{image_url}'..")

    req = Request(image_url, origin_req_host="houseofgord.com")
    req.add_header("Referer", "https://www.houseofgord.com/")
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    )

    image_data = urlopen(req).read()
    image_data_b64 = base64.b64encode(image_data).decode("utf-8")

    performer: Performer = {
        "name": name,
        "disambiguation": "House of Gord",
        "gender": "FEMALE",
        "urls": [model["url"]],
        "aliases": aliases,
        "image": image_data_b64,
        "created_at": now,
        "updated_at": now,
    }

    name_sanitised = "".join(x for x in name if (x.isalnum() or x in "._- "))
    output_file = output_dir / f"{name_sanitised}.json"

    print(f"Writing '{output_file}'..")
    with open(output_file, "w") as f:
        json.dump(performer, f)

    sleep(0.1)
