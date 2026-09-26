"""Build the reproducible ZoroLogistics silver tables."""

from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from zoro import data



def load_or_generate():
    """Load Week 1 CSVs, or generate the same raw data from seed 42."""
    data_dir = REPO_ROOT / "data"
    shipments_path = data_dir / "shipments.csv"

    if shipments_path.exists():
        raw = pd.read_csv(
            shipments_path,
            parse_dates=["planned_departure", "planned_arrival", "actual_arrival"],
        )
        lanes = pd.read_csv(data_dir / "lanes.csv")
        carriers = pd.read_csv(data_dir / "carriers.csv")
        print("Loaded raw CSVs from data/")
    else:
        raw = data.shipments(100_000, seed=42)
        lanes = data.lanes(20, seed=11)
        carriers = data.carriers(20, seed=7)
        print("Raw CSVs not found; generated data with seed 42")

    return raw, lanes, carriers



def clean(raw, lanes):
    """Apply the Week 2 cleaning decisions and return cleaned tables plus counts."""
    before_rows = len(raw)
    n_nan_weight = int(raw["weight_kg"].isna().sum())
    n_nan_dist = int(lanes["distance_km"].isna().sum())

    shipments = raw.drop_duplicates().copy()
    n_dupes_removed = before_rows - len(shipments)

    shipments["weight_kg"] = shipments["weight_kg"].fillna(
        shipments.groupby("commodity")["weight_kg"].transform("median")
    )

    cleaned_lanes = lanes.copy()
    cleaned_lanes["distance_km"] = cleaned_lanes["distance_km"].fillna(
        cleaned_lanes["distance_km"].median()
    )

    n_bad_weight = int((shipments["weight_kg"] <= 0).sum())
    shipments = shipments[shipments["weight_kg"] > 0].reset_index(drop=True)

    n_bad_transit = int(
        (shipments["planned_arrival"] <= shipments["planned_departure"]).sum()
    )
    shipments = shipments[
        shipments["planned_arrival"] > shipments["planned_departure"]
    ].reset_index(drop=True)

    counts = {
        "before_rows": before_rows,
        "duplicates_removed": n_dupes_removed,
        "weight_nans_imputed": n_nan_weight,
        "distance_nans_imputed": n_nan_dist,
        "non_positive_weights_dropped": n_bad_weight,
        "bad_transit_rows_dropped": n_bad_transit,
    }
    return shipments, cleaned_lanes, counts



def validate(shipments, lanes, carriers):
    """Run the 12 Week 2 checks and return their results."""
    results = []

    def check(name, condition):
        passed = bool(condition)
        results.append((name, passed))
        print(("PASS  " if passed else "FAIL  ") + name)

    check("no duplicate rows", shipments.duplicated().sum() == 0)
    check("no NaN weight_kg", shipments["weight_kg"].isna().sum() == 0)
    check("all weights positive", (shipments["weight_kg"] > 0).all())
    check("no NaN delay_hours", shipments["delay_hours"].isna().sum() == 0)
    check("no NaN is_on_time", shipments["is_on_time"].isna().sum() == 0)
    check("value_usd non-negative", (shipments["value_usd"] >= 0).all())
    check(
        "carrier_id referential integrity",
        shipments["carrier_id"].isin(carriers["carrier_id"]).all(),
    )
    check(
        "lane_id referential integrity",
        shipments["lane_id"].isin(lanes["lane_id"]).all(),
    )
    check(
        "is_on_time is boolean",
        set(shipments["is_on_time"].unique()) <= {True, False},
    )
    check(
        "delay_hours within plausible range",
        shipments["delay_hours"].between(-48, 240).all(),
    )
    check(
        "planned_arrival after departure",
        (shipments["planned_arrival"] > shipments["planned_departure"]).all(),
    )
    check("lanes have no NaN distance", lanes["distance_km"].isna().sum() == 0)

    passed = sum(ok for _, ok in results)
    print(f"CHECKS_PASSED: {passed} of {len(results)}")
    return results



def save_silver(shipments, lanes, carriers, counts, results):
    """Write silver CSVs and the validation report."""
    silver_dir = REPO_ROOT / "data" / "silver"
    silver_dir.mkdir(parents=True, exist_ok=True)

    shipments.to_csv(silver_dir / "shipments_silver.csv", index=False)
    lanes.to_csv(silver_dir / "lanes_silver.csv", index=False)
    carriers.to_csv(silver_dir / "carriers_silver.csv", index=False)

    passed = sum(ok for _, ok in results)
    report = [
        "# Silver Pipeline - Cleaning Report",
        "",
        "- Seed: 42",
        f"- Input rows: {counts['before_rows']:,}",
        f"- Duplicates removed: {counts['duplicates_removed']:,}",
        f"- weight_kg NaNs imputed (median by commodity): {counts['weight_nans_imputed']:,}",
        f"- distance_km NaNs imputed (median): {counts['distance_nans_imputed']:,}",
        f"- Non-positive weights dropped: {counts['non_positive_weights_dropped']:,}",
        f"- Bad transit rows dropped: {counts['bad_transit_rows_dropped']:,}",
        f"- Output rows: {len(shipments):,}",
        "",
        "## Validation",
        "",
        f"- Checks passed: {passed} of {len(results)}",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    report.extend(
        f"| {name} | {'PASS' if ok else 'FAIL'} |" for name, ok in results
    )
    (silver_dir / "validation-report.md").write_text("\n".join(report) + "\n")
    print("Saved silver tables and validation report to", silver_dir)



def main():
    raw, lanes, carriers = load_or_generate()
    shipments, cleaned_lanes, counts = clean(raw, lanes)
    results = validate(shipments, cleaned_lanes, carriers)

    if not all(ok for _, ok in results):
        raise SystemExit("Validation failed; silver files were not saved.")

    save_silver(shipments, cleaned_lanes, carriers, counts, results)
    print("SILVER_ROW_COUNT:", len(shipments))


if __name__ == "__main__":
    main()
