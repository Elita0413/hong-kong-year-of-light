# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

import json
import math
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


FILE = "nasa-power-hong-kong-solar-2025.json"
PICTURE = "year-of-light.png"

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"


def load_data(path):
    content = json.loads(
        path.read_text(encoding="utf-8")
    )

    values = content["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]

    rows = []

    for date_text, raw_value in sorted(values.items()):
        value = float(raw_value)

        # NASA POWER uses -999 as its missing-data value.
        if value == -999:
            continue

        date = datetime.strptime(
            date_text,
            "%Y%m%d"
        )

        day_of_year = date.timetuple().tm_yday

        rows.append(
            (day_of_year, value)
        )

    return rows


def draw_day(ax, day_of_year, value, maximum):
    """Turn one day's solar radiation into one radial bar."""

    angle = (
        2 * math.pi
        * (day_of_year - 1)
        / 365
    )

    inner_radius = 1.0

    height = (
        value / maximum
        * 5.0
    )

    ax.bar(
        angle,
        height,
        width=2 * math.pi / 365 * 0.82,
        bottom=inner_radius,
        alpha=0.8,
    )


def main():
    rows = load_data(DATA)

    print(f"{len(rows)} valid daily values")
    print("First value:", rows[0])
    print("Value type:", type(rows[0][1]))

    maximum = max(
        value for _, value in rows
    )

    fig = plt.figure(
        figsize=(10, 10)
    )

    ax = fig.add_subplot(
        111,
        projection="polar"
    )

    # Start January at the top.
    ax.set_theta_offset(
        math.pi / 2
    )

    # Move clockwise.
    ax.set_theta_direction(-1)

    for day, value in rows:
        draw_day(
            ax,
            day,
            value,
            maximum
        )

    # Month labels.
    month_starts = [
        1, 32, 60, 91,
        121, 152, 182, 213,
        244, 274, 305, 335
    ]

    month_names = [
        "JAN", "FEB", "MAR", "APR",
        "MAY", "JUN", "JUL", "AUG",
        "SEP", "OCT", "NOV", "DEC"
    ]

    month_angles = [
        2 * math.pi * (day - 1) / 365
        for day in month_starts
    ]

    ax.set_xticks(month_angles)
    ax.set_xticklabels(month_names)

    ax.set_yticks([])

    ax.set_title(
        "A Year of Light — Hong Kong, 2025",
        pad=30
    )

    ax.text(
        0,
        0,
        "SOLAR\nRADIATION",
        ha="center",
        va="center"
    )

    OUT.mkdir(exist_ok=True)

    fig.savefig(
        OUT / PICTURE,
        dpi=200,
        bbox_inches="tight"
    )

    print(
        f"Saved out/{PICTURE}"
    )

    plt.show()


if __name__ == "__main__":
    main()