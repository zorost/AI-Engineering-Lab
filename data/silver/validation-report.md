# Silver Pipeline - Cleaning Report

- Seed: 42
- Input rows: 100,200
- Duplicates removed: 200
- weight_kg NaNs imputed (median by commodity): 301
- distance_km NaNs imputed (median): 1
- Non-positive weights dropped: 0
- Bad transit rows dropped: 0
- Output rows: 100,000

## Validation

- Checks passed: 12 of 12

| Check | Result |
|---|---|
| no duplicate rows | PASS |
| no NaN weight_kg | PASS |
| all weights positive | PASS |
| no NaN delay_hours | PASS |
| no NaN is_on_time | PASS |
| value_usd non-negative | PASS |
| carrier_id referential integrity | PASS |
| lane_id referential integrity | PASS |
| is_on_time is boolean | PASS |
| delay_hours within plausible range | PASS |
| planned_arrival after departure | PASS |
| lanes have no NaN distance | PASS |
