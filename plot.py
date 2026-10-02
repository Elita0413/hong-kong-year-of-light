# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
A Year of Light

NASA POWER daily solar-radiation data
for Hong Kong, 2025.

Visual logic:
    day of year       -> angular position
    solar radiation   -> radial length
"""

import json
import math
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl


# ============================================================
# PROJECT SETTINGS
# ============================================================

FILE = "nasa-power-hong-kong-solar-2025.json"
PICTURE = "year-of-light.png"


# ============================================================
# VISUAL SETTINGS
# ============================================================

# Composition
INNER_RADIUS = 1.65
MAX_LENGTH = 4.7
LABEL_RADIUS = 6.35

# Colours
BACKGROUND = "#F5F1E8"
COLOR_STOPS = [
    "#F2D7A7",
    "#E9A05B",
    "#D9784E",
    "#B94F3A",
    "#7F2F2A",
]
TEXT_COLOR = "#1D1D1B"
SECONDARY_TEXT = "#746C62"
CENTRE_COLOR = "#F5F1E8"

SOLAR_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "solar_light",
    COLOR_STOPS
)

# Typography
TITLE_SIZE = 26
CENTRE_MAIN_SIZE = 22
CENTRE_SECONDARY_SIZE = 13
MONTH_SIZE = 8.5
SMALL_SIZE = 8


# ============================================================
# PATHS
# ============================================================

HERE = Path(__file__).parent

DATA = HERE / "data" / FILE
OUT = HERE / "out"


# ============================================================
# DATA LOADING
# ============================================================

def load_data(path):
    """
    Read NASA POWER JSON data.

    Returns:
        [
            (day_of_year, solar_radiation),
            ...
        ]
    """

    content = json.loads(
        path.read_text(encoding="utf-8")
    )

    values = (
        content[
            "properties"
        ][
            "parameter"
        ][
            "ALLSKY_SFC_SW_DWN"
        ]
    )

    rows = []

    for date_text, raw_value in sorted(values.items()):

        value = float(raw_value)

        # Ignore NASA POWER missing/invalid negative values.
        if value < 0:
            continue

        date = datetime.strptime(
            date_text,
            "%Y%m%d"
        )

        day_of_year = date.timetuple().tm_yday

        rows.append(
            (
                day_of_year,
                value
            )
        )

    return rows


# ============================================================
# DRAW ONE DAY
# ============================================================

def draw_day(ax, day_of_year, value, maximum):
    """
    Draw one day as one radial mark.

    Data mapping:

        day_of_year -> angle
        value       -> length
    """

    # --------------------------------------------------------
    # DAY -> ANGLE
    # --------------------------------------------------------

    angle = (
        2 * math.pi
        * (day_of_year - 1)
        / 365
    )

    # --------------------------------------------------------
    # SOLAR RADIATION -> LENGTH
    # --------------------------------------------------------

    height = (
        value / maximum
        * MAX_LENGTH
    )

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    color = SOLAR_CMAP(
        value / maximum
    )

    ax.bar(
        angle,
        height,
        width=(
        2 * math.pi / 365 * 0.78
        ),
        bottom=INNER_RADIUS,
        color=color,
        alpha=0.82,
        linewidth=0,
        align="edge",
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # LOAD DATA
    # ========================================================

    rows = load_data(DATA)

    if not rows:
        raise ValueError(
            "No valid data was found."
        )

    print(
        f"Loaded {len(rows)} valid daily values."
    )

    print(
        f"First value: {rows[0]}"
    )

    print(
        f"Value type: {type(rows[0][1])}"
    )

    minimum = min(
        value for _, value in rows
    )

    maximum = max(
        value for _, value in rows
    )

    print(
        f"Solar radiation range: "
        f"{minimum:.2f}–{maximum:.2f} MJ/m²/day"
    )

    # ========================================================
    # FIGURE
    # ========================================================

    fig = plt.figure(
        figsize=(10, 10),
        facecolor=BACKGROUND
    )

    ax = fig.add_subplot(
        111,
        projection="polar"
    )

    ax.set_facecolor(BACKGROUND)

    # ========================================================
    # POLAR ORIENTATION
    # ========================================================

    # January begins at the top.
    ax.set_theta_offset(
        math.pi / 2
    )

    # Move clockwise.
    ax.set_theta_direction(-1)

    # ========================================================
    # DRAW ALL DAYS
    # ========================================================

    for day, value in rows:

        draw_day(
            ax,
            day,
            value,
            maximum
        )

    # ========================================================
    # COMPOSITION
    # ========================================================

    ax.set_ylim(
        0,
        LABEL_RADIUS + 0.65
    )

    # Remove default polar chart elements.
    ax.set_xticks([])
    ax.set_yticks([])

    ax.spines["polar"].set_visible(False)

    # ========================================================
    # MONTH LABELS
    # ========================================================

    month_starts = [
        1,
        32,
        60,
        91,
        121,
        152,
        182,
        213,
        244,
        274,
        305,
        335
    ]

    month_names = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC"
    ]

    month_angles = [
        2 * math.pi
        * (day - 1)
        / 365
        for day in month_starts
    ]

    for angle, name in zip(
        month_angles,
        month_names
    ):

        ax.text(
            angle,
            LABEL_RADIUS,
            name,
            ha="center",
            va="center",
            fontsize=MONTH_SIZE,
            color=SECONDARY_TEXT,
            fontweight="medium"
        )

    # ========================================================
    # CENTRE DISK
    # ========================================================

    # Cover the inside of the radial chart with a clean disk.
    inner_circle = plt.Circle(
        (0, 0),
        INNER_RADIUS - 0.02,
        transform=ax.transData._b,
        facecolor=CENTRE_COLOR,
        edgecolor="none",
        zorder=10
    )

    ax.add_artist(
        inner_circle
    )

    # ========================================================
    # CENTRE INFORMATION
    # ========================================================

    ax.text(
        0,
        0,
        "HONG KONG · 2025\n365 DAILY VALUES",
        ha="center",
        va="center",
        multialignment="center",
        fontsize=9,
        fontweight="medium",
        color=TEXT_COLOR,
        linespacing=1.6,
        zorder=20
    )

    # ========================================================
    # TOP TITLE
    # ========================================================

    # Instead of putting a second large title directly
    # above the chart, create a smaller editorial header.

    fig.text(
        0.08,
        0.94,
        "A YEAR OF LIGHT",
        ha="left",
        va="center",
        fontsize=TITLE_SIZE,
        fontweight="bold",
        color=TEXT_COLOR
    )

    fig.text(
        0.08,
        0.913,
        "SURFACE SOLAR RADIATION · NASA POWER",
        ha="left",
        va="center",
        fontsize=SMALL_SIZE,
        color=SECONDARY_TEXT
    )

    # ========================================================
    # FOOTER
    # ========================================================

    fig.text(
        0.08,
        0.045,
        "365 DAILY VALUES",
        ha="left",
        va="center",
        fontsize=SMALL_SIZE,
        color=SECONDARY_TEXT
    )

    fig.text(
        0.92,
        0.045,
        "MJ/m²/day",
        ha="right",
        va="center",
        fontsize=SMALL_SIZE,
        color=SECONDARY_TEXT
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    OUT.mkdir(
        exist_ok=True
    )

    output_path = OUT / PICTURE

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        facecolor=BACKGROUND
    )

    print(
        f"Saved: {output_path}"
    )

    plt.show()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()