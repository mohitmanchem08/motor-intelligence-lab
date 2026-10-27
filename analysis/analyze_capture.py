#!/usr/bin/env python3
"""Validate and summarize Motor Intelligence Lab CSV captures."""

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

REQUIRED = (
    "time_ms", "ax_g", "ay_g", "az_g",
    "gx_dps", "gy_dps", "gz_dps", "current_a", "adc_raw",
)


def load_rows(path: Path):
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        lines = (line for line in handle if line.strip() and not line.startswith("#"))
        reader = csv.DictReader(lines)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        missing = set(REQUIRED) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            try:
                parsed = {key: float(row[key]) for key in REQUIRED}
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on data row {line_number}") from exc
            if not all(math.isfinite(value) for value in parsed.values()):
                raise ValueError(f"Non-finite value on data row {line_number}")
            rows.append(parsed)
    if len(rows) < 2:
        raise ValueError("At least two numeric samples are required")
    times = [row["time_ms"] for row in rows]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("time_ms must be strictly increasing")
    return rows


def rms(values):
    return math.sqrt(sum(value * value for value in values) / len(values))


def summarize(rows):
    times = [row["time_ms"] for row in rows]
    intervals = [b - a for a, b in zip(times, times[1:])]
    current = [row["current_a"] for row in rows]
    acceleration = [
        math.sqrt(row["ax_g"] ** 2 + row["ay_g"] ** 2 + row["az_g"] ** 2)
        for row in rows
    ]
    return {
        "sample_count": len(rows),
        "duration_s": (times[-1] - times[0]) / 1000.0,
        "sample_interval_ms_mean": statistics.mean(intervals),
        "sample_interval_ms_min": min(intervals),
        "sample_interval_ms_max": max(intervals),
        "current_a_mean": statistics.mean(current),
        "current_a_rms": rms(current),
        "current_a_min": min(current),
        "current_a_max": max(current),
        "acceleration_magnitude_g_rms": rms(acceleration),
        "note": "Current estimates depend on calibration; inspect raw data before interpreting.",
    }


def make_plot(rows, output: Path):
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Install matplotlib from analysis/requirements.txt to plot") from exc
    t = [row["time_ms"] / 1000.0 for row in rows]
    current = [row["current_a"] for row in rows]
    accel = [
        math.sqrt(row["ax_g"] ** 2 + row["ay_g"] ** 2 + row["az_g"] ** 2)
        for row in rows
    ]
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10, 6))
    axes[0].plot(t, current)
    axes[0].set_ylabel("Estimated current (A)")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(t, accel)
    axes[1].set_ylabel("Acceleration magnitude (g)")
    axes[1].set_xlabel("Elapsed time (s)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--out", type=Path, help="write JSON summary")
    parser.add_argument("--plot", type=Path, help="write current/acceleration plot")
    args = parser.parse_args()
    rows = load_rows(args.csv)
    result = summarize(rows)
    print(json.dumps(result, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.plot:
        make_plot(rows, args.plot)


if __name__ == "__main__":
    main()
