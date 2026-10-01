# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

from pathlib import Path
import requests

URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
    "?parameters=ALLSKY_SFC_SW_DWN"
    "&community=RE"
    "&longitude=114.1694"
    "&latitude=22.3193"
    "&start=20250101"
    "&end=20251231"
    "&format=JSON"
    "&time-standard=LST"
)

FILE = "nasa-power-hong-kong-solar-2025.json"

HERE = Path(__file__).parent
DATA = HERE / "data"


def fetch(url, path):
    """Fetch the data once and save the raw response."""

    if path.exists():
        print(
            f"{path.name} is already here. "
            "Delete it if you really need to fetch again."
        )
        return path

    DATA.mkdir(exist_ok=True)

    print(f"Fetching:\n{url}")

    response = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "SD5913 student"}
    )

    response.raise_for_status()

    # Save exactly what NASA returned.
    path.write_bytes(response.content)

    print(f"Saved {path}")

    return path


if __name__ == "__main__":
    fetch(URL, DATA / FILE)