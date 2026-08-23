#!/usr/bin/env python3
"""Reproducible RSSI sample plot from data/sample_rssi.csv."""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample_rssi.csv"


def load_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    rows = load_rows(CSV_PATH)
    assert rows, "sample CSV is empty"
    # ASCII sparkline so the example runs without a display/GUI backend.
    vals = [float(r["rssi_dbm"]) for r in rows]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    blocks = " .:-=+*#%@"
    line = "".join(blocks[min(len(blocks) - 1, int((v - lo) / span * (len(blocks) - 1)))] for v in vals)
    print(f"loaded {len(rows)} samples from {CSV_PATH.relative_to(ROOT)}")
    print(f"rssi_dbm range [{lo}, {hi}]")
    print(line)
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not installed; skipped PNG (ASCII plot above is enough)")
        return
    xs = [float(r["timestamp_s"]) for r in rows]
    plt.figure(figsize=(8, 3))
    plt.plot(xs, vals, marker="o")
    plt.xlabel("time (s)")
    plt.ylabel("RSSI (dBm)")
    plt.title("Sample RSSI")
    plt.grid(True, alpha=0.3)
    out = ROOT / "examples" / "sample_rssi.png"
    plt.tight_layout()
    plt.savefig(out, dpi=120)
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
