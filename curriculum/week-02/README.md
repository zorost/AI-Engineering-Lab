# Week 02: Data Engineering & SQL for AI

> Part of AI Engineering Lab · Week 02 of 24 · Section: Foundations · Category: Data & SQL
> 🎯 Use case: Clean and profile the raw shipment dataset into an analytics-ready "silver" table.

## The problem

ZoroLogistics just generated 100,000+ shipment rows, and, because the generator planted its flaws on purpose, the data is *dirty in exactly the ways real freight data is dirty.* There are **200 duplicate shipment rows** (the same truck counted twice), **301 missing `weight_kg` values**, and **1 missing lane `distance_km`**. If any downstream consumer trusts this raw file, the damage compounds silently: duplicates inflate the on-time rate and every count; missing distances become a hole the Week 3 ETA model trains on; missing weights break invoice math. Worse, *nobody has written down what "clean" even means*, so two analysts will "fix" the same file two different ways and never agree on a number.

Without this week, ZoroLogistics has a data swamp: every model downstream inherits the raw file's quality, and "the AI gives wrong answers" is blamed on the model when the real root cause is the table it read. With this week, the company gets a **silver table**, cleaned, conformed, and gated by a re-runnable validation suite, plus the SQL skills to *ask questions* of it. This is the week Zorost's discipline file calls the single most common root cause behind wrong AI answers: **data engineering**. A model is only as good as the table it reads, and starting now, you own that table.

## Objectives

- [ ] By Friday you can load the raw `shipments.csv` and find, document, and fix every planted data-quality issue (duplicates, `NaN` weights, `NaN` distances).
- [ ] By Friday you can write a validation suite of at least 10 explicit, pandera-style checks that a "silver" table must pass.
- [ ] By Friday you can answer analytics questions in SQL (DuckDB): on-time rate by carrier/lane/month, window functions, and top-lane analysis.
- [ ] By Friday you can ship a cleaned silver dataset plus a profile report that documents every cleaning decision and its rationale.

## Day-by-day plan

| Day | Study | Run | Ship | Time |
|---|---|---|---|---|
| **Mon** | Data-quality concepts; read [`reference/knowledge-base/02-ml-dl-fundamentals.md`](../../reference/knowledge-base/02-ml-dl-fundamentals.md) §2 (splits) for the "no leakage" rule | pandas refresher: `filter`, `groupby`, `merge`, `dtypes` | Notes on what "clean" means | ~2 h |
| **Tue** | Missing data, outliers, profiling | `01-pandas-cleaning.ipynb` Steps 1 to 3 (profile + find planted issues) | Document 5 data issues with counts | ~2.5 h |
| **Wed** | SQL joins, aggregations, window functions | `02-sql-with-duckdb.ipynb` (on-time by carrier/lane/month, windows, top lanes) | Recorded SQL results | ~2.5 h |
| **Thu** | Data validation; explicit invariants | `01-pandas-cleaning.ipynb` Step 5 (the 12-check gate) | A passing validation suite (12/12) | ~2 h |
| **Fri** | Dataset versioning and reproducibility | Re-run clean→validate→save end-to-end; write the report | Silver tables + validation report committed | ~3 h |
| **Sat** | Review the week | Take the quiz (`quiz.md`, 8/10 to pass) | Record the score in Notes | ~45 min |

## Concepts

The discipline file for the next three weeks is [`reference/knowledge-base/02-ml-dl-fundamentals.md`](../../reference/knowledge-base/02-ml-dl-fundamentals.md), but this week's real subject is the **data path underneath every model**. Read it through one lens: *a metric is only as honest as the data that produced it.* If your table has duplicate rows, your on-time rate is inflated; if a third of lane distances are `NaN`, your ETA model trains on a hole. Cleaning is not janitorial work done before the "real" AI, it *is* the AI engineering.

### 1. pandas: filter, group, join, pivot, dtypes

pandas is how you **shape** a table. The five verbs that cover most of it: `df[df.col > 0]` to **filter**, `df.groupby("commodity")["weight_kg"].transform("median")` to **group** and fill within groups, `df.merge(lanes, on="lane_id", how="left")` to **join** (re-attach a foreign key's master data), `df.pivot_table(...)` to **pivot** a long table wide, and `df.dtypes` to inspect physical types. The cleaning notebook uses all of them: it merges `shipments` with `lanes` and `carriers`, then uses a group-aware median to impute missing weight.

### 2. Missing data, outliers, and data quality

Real data has three species of defect. **Missing data** (`NaN`) needs a decision: drop the row, impute a value, or carry it forward, and the decision must be *recorded*. **Outliers** (a shipment "delayed" 200 hours, or a weight of −5 kg) can be genuine extremes or corruption; profiling tells you which. **Structural defects** (duplicates, a `planned_arrival` before its `planned_departure`, a foreign key pointing nowhere) are the most dangerous because they look valid. The generator plants the first and third; profiling surfaces all of them.

| Species | Example in this data | Typical fix |
|---|---|---|
| Missing | `NaN` `weight_kg` (301), `NaN` `distance_km` (1) | Impute (group-aware median) or drop, then record it |
| Outlier | `delay_hours` up to 227.88 h | Profile first; decide genuine extreme vs. corruption |
| Structural | duplicate rows (200), FK pointing nowhere | Deduplicate; enforce referential integrity |

### 3. Profiling and summary statistics

Profile before you fix. `df.shape`, `df.dtypes`, `df.describe()`, and `df.isna().sum()` answer *how many, where, and how extreme* before you touch a value. The notebook's Step 1 prints a numeric summary of `weight_kg`, `value_usd`, and `delay_hours`, then Step 3 digs deeper: non-positive weights, impossible transit rows, and the on-time share. You cannot choose an imputation strategy until you know the counts.

### 4. SQL with DuckDB: joins, aggregations, window functions

Pandas helps you shape a table. **SQL helps you ask questions about it.** DuckDB runs SQL directly on your pandas tables without a separate database server.

Imagine these two small tables:

`shipments`:

| shipment_id | carrier_id | is_on_time |
|---|---|---|
| S001 | C01 | True |
| S002 | C02 | False |

`carriers`:

| carrier_id | carrier_name |
|---|---|
| C01 | Fast Trucking |
| C02 | North Freight |

The shipment table stores `carrier_id`, not the carrier name. The ID is the link between the tables.

| Verb | What it does | Week 2 example |
|---|---|---|
| **Join** | Connect related tables using a shared ID | Add carrier details to shipments using `carrier_id` |
| **Aggregate** | Group rows and calculate a summary | Calculate average on-time rate per carrier |
| **Window** | Calculate group information while keeping each row | Rank carriers inside each month |

A **window function** is different from `GROUP BY`:

- `GROUP BY` combines many rows into one row per group.
- A window function calculates across a group but keeps the original rows.

Use `GROUP BY` to ask, “What is the rate per carrier?” Use a window function to ask,
“Which carriers are in the top two each month?”

**Join example:**

```sql
SELECT s.shipment_id, c.carrier_name
FROM shipments s
JOIN carriers c ON s.carrier_id = c.carrier_id
```

This reads as: “Take each shipment, find the carrier with the same ID, and show the carrier name.”

**Aggregate example:**

```sql
SELECT carrier_id, AVG(CAST(is_on_time AS INT)) AS on_time_rate
FROM shipments
GROUP BY carrier_id
```

`True` becomes `1` and `False` becomes `0`. If a carrier has `[True, True, False]`, its rate is `(1 + 1 + 0) / 3 = 0.667`, or 66.7%.

**Window example:**

```sql
RANK() OVER (PARTITION BY month ORDER BY on_time_rate DESC)
```

This means: “For each month, put the carrier with the highest rate in position 1.” Unlike `GROUP BY`, it can keep the carrier’s row while adding its rank.

### 5. Data validation (pandera) with explicit checks

A cleaned table is a **claim**. Validation is the **proof** that the table is safe to use.

The notebook runs 12 checks, including:

- no duplicate rows;
- no missing weights;
- all weights are positive;
- every `carrier_id` and `lane_id` points to a real record;
- `is_on_time` is a boolean;
- `delay_hours` is within the allowed range.

Each check prints `PASS` or `FAIL`. The table is not ready until all 12 checks pass.
Pandera is a library that can turn these rules into a reusable dataframe schema.

Think of validation like an inspection before a truck leaves the warehouse. For example:

```python
assert ships["weight_kg"].notna().all()
```

This means: “Every shipment must have a weight.” If even one weight is missing, the check fails. A failing check does not mean Python is broken; it means the data is not ready yet.

Another check might be:

```python
assert not ships.duplicated().any()
```

This means: “There must not be any completely repeated shipment rows.” The validation gate prevents dirty data from silently moving to the next step.

### 6. Dataset versioning and reproducibility

Week 1 made the raw data reproducible with a seed. Week 2 applies the same idea to
cleaning: record the steps so someone can repeat `raw -> silver` and get the same result.

In the medallion system used later in the course:

- **Bronze** means raw data.
- **Silver** means cleaned and validated data.
- **Gold** means summarized data ready for people or applications.

Treat silver as a **contract**, not just a folder. It must have a known schema, meet
known rules, and pass the validation suite.

Here is the complete idea in plain language:

```text
raw CSV files
    -> inspect and count problems
    -> remove duplicates and fill approved missing values
    -> run validation checks
    -> save the silver tables
```

The cleaning recipe is the list of decisions in the middle. For example, “fill missing weight with the median for that commodity” is a recipe. If you write that decision down, another engineer can repeat it. If you only edit the file by hand, nobody knows exactly what happened.

**Worked example.** With seed 42:

- the raw table has 100,200 shipment rows;
- removing 200 duplicates leaves 100,000 rows;
- 301 missing weights are filled with the median for their commodity;
- 1 missing lane distance is filled with the overall lane median;
- no rows are removed for impossible weights or dates.

The result is a silver table with exactly 100,000 shipments. Record these before-and-
after numbers in the report so another person can audit the cleaning.

The word **versioning** means keeping a record of which data and which steps produced the result. For this week, record the seed, the original row count, the number of rows removed, the missing-value counts, and the final row count. That record lets you compare a future version with this one.

**SQL example.** `is_on_time` is `True` or `False`. SQL can cast these to `1` or `0`:

```sql
AVG(CAST(is_on_time AS INT))
```

The average is the on-time rate. For example, 79,566 on-time shipments out of 100,000
gives `0.7957`, or 79.6%.

**Window example.** `GROUP BY` can show the rate for each month. A window function can
then rank carriers inside each month, answering “who is leading when?”

```mermaid
%%{init:{"theme":"base","fontFamily":"Helvetica Neue,Helvetica,Arial,sans-serif","flowchart":{"curve":"basis","padding":14,"nodeSpacing":45,"rankSpacing":55},"themeVariables":{"fontSize":"15px","background":"#FFFFFF","primaryColor":"#EEF2F7","primaryTextColor":"#14213D","primaryBorderColor":"#14213D","secondaryColor":"#FFF1E3","secondaryTextColor":"#14213D","tertiaryColor":"#E7F4F1","tertiaryTextColor":"#14213D","lineColor":"#64748B","textColor":"#14213D","edgeLabelBackground":"#FFFFFF","clusterBkg":"#F5F8FC","clusterBorder":"#94A3B8","nodeBorder":"#14213D","mainBkg":"#EEF2F7","titleColor":"#14213D"}}}%%
flowchart LR
    A[raw shipments.csv<br/>100,200 rows] --> B[Profile<br/>shape, dtypes, describe, isna]
    B --> C[Find planted issues<br/>200 dupes · 301 NaN weight · 1 NaN distance]
    C --> D[Clean<br/>drop dupes · impute weight by commodity median<br/>impute distance by global median]
    D --> E["Validate<br/>12 checks: dupes, NaNs, referential integrity, ranges"]
    E -->|all PASS| F[silver/ tables + validation-report.md]
    E -->|any FAIL| C
    F --> G[DuckDB SQL<br/>joins, aggregates, windows]
```

### How it breaks

Cleaning breaks when you **impute before profiling** (filling with the global median when a per-group median is correct, or worse, filling *before* counting so you lose the audit trail). It breaks when you **drop duplicates without recording how many**, the downstream count changes and nobody can say why. It breaks when a **validation check silently passes** because you tested the wrong invariant (e.g. checking "no `NaN`" on a column you just imputed, which is circular). It breaks when you **normalize on the full dataset instead of train-only**, that leakage decision belongs to Week 3, but the habit starts here. And it breaks when you treat cleaning as a one-off: without a re-runnable suite, the next batch arrives dirty and the "silver" contract evaporates. The fix in every case is the same: a recorded recipe with a gate that fails loudly.

For deeper dives: the discipline file's "systems-engineering spine" (verification is where the checks belong) and [`reference/knowledge-base/02-ml-dl-fundamentals.md`](../../reference/knowledge-base/02-ml-dl-fundamentals.md) §2 for the time-aware split you'll need next week.

## Notebook walkthrough

**`notebooks/01-pandas-cleaning.ipynb`** loads the committed CSVs (or regenerates them in-memory if `data/` is missing), then profiles: Step 1 prints `shape`, `dtypes`, a `describe()` of the three numeric columns, and per-column null counts. Step 2 counts the three planted issues precisely. Step 3 finds the *un*planted ones, non-positive weights, impossible transit rows, and the on-time share. Step 4 performs the four cleaning decisions (drop dupes, impute weight by commodity median, impute distance by median, defensive drops) and prints each count. Step 5 runs the **12-check gate** and prints `CHECKS_PASSED: 12 of 12`. Step 6 writes `data/silver/` (three tables) plus `validation-report.md`. The final cell prints **`CHECKS_PASSED`** and **`SILVER_ROW_COUNT`**, the two numbers you record.

**`notebooks/02-sql-with-duckdb.ipynb`** installs duckdb via `%pip`, registers the three tables with `con.register(...)`, then runs five queries: the company-wide on-time rate; top-5 carriers and bottom-5 lanes by on-time rate; on-time rate by month (`date_trunc('month', planned_departure)`); a **window function** (`RANK() OVER (PARTITION BY month ORDER BY on_time_rate DESC)` with `QUALIFY rnk <= 2`) for top-2 carriers per month; and a top-lane analysis (shipments, avg `delay_hours`, summed `value_usd`). The final cell prints **`OVERALL_ON_TIME_RATE`**, expect ≈ 0.7957. "Correct" output: 12/12 checks pass, silver row count 100,000, and the on-time rate ≈ 79.6%.

Cells to modify: the Standard exercise changes Step 4's cleaning decisions (try a *global* median for weight and note how the group-aware one differs) and documents the un-planted defects surfaced in Step 3's deeper profiling. The Stretch exercise rewrites the on-time-by-month query with a window function and adds an `np.allclose` assertion against the `GROUP BY` result. The validation Step 5 is the one cell you must *not* loosen, if any check fails, the table is not silver. If the silver row count prints 100,200 you forgot `drop_duplicates()`; if the on-time rate prints 1.0 you cast the boolean wrong. The Friday profile report is simply these numbers written down with their rationale, one line per decision.

## The use case (Friday)

**Deliverable:** a `data/silver/` directory with the cleaned shipment table, a `validation-report.md` listing 12 checks and their pass/fail, and a profile report documenting every cleaning decision (what you found, what you did, why).

**Zorost gate:** a stranger can re-run your cleaning notebook from the raw CSV, reproduce your exact silver table, and read your report to see *what the cleaner did*, which rows it dropped, which `NaN`s it imputed (and with what), and which checks gate the result. You can show the before/after numbers (duplicate count, `NaN` counts, row count) and defend each decision in one sentence.

**Stretch variant:** replace the notebook's hand-rolled `check()` list with an actual **pandera** `DataFrameSchema`, and make the pipeline a single runnable `data/make_silver.py` script, so `python make_silver.py` regenerates, cleans, validates, and writes silver in one command.

## Common pitfalls

| Pitfall | Why it happens | Fix |
|---|---|---|
| Imputing before counting `NaN`s | Eager to "fix" before profiling | Profile first; record the count, then impute, then re-check |
| `groupby(...).transform("median")` returning `NaN` for a group | A group with *all*-`NaN` values | Fall back to the global median for empty groups |
| Dropping duplicates silently | No before/after count | Print and record `before_rows - len(ships)` |
| Circular validation checks | Checking "no `NaN`" *after* filling | Validate the property that matters, and keep one raw `NaN` count from before imputation |
| `CAST(is_on_time AS INT)` failing | The column is boolean but the engine treats it as text | Cast explicitly to `INT` (DuckDB) before `AVG` |
| Referential-integrity check skipping rows | `isin()` evaluated on the wrong table's key | Join on the *foreign* key against the master's *primary* key |
| Treating "silver" as a folder, not a contract | Naming convention without a gate | Re-run the 12-check suite on any new batch; fail the build on any FAIL |

## Glossary

- **Bronze / silver / gold**: the medallion tiers: raw landing data, cleaned/conformed data, aggregated data for consumption.
- **Profiling**: measuring shape, dtypes, summary stats, and missingness before cleaning.
- **Imputation**: filling a missing value with a computed one (e.g. a median), recorded as a decision.
- **Duplicate row**: an identical row repeated, inflating every downstream count.
- **Foreign key / primary key**: a column referencing / uniquely identifying rows in another table.
- **Referential integrity**: every foreign-key value matches an existing primary key.
- **Join**: combining rows from two tables on a shared key.
- **Aggregation**: collapsing rows into groups and reducing (count, avg, sum).
- **Window function**: a value computed across a group while keeping every row (e.g. `RANK() OVER`).
- **Validation suite**: executable invariants a table must pass to be considered "clean."
- **DuckDB**: an embedded, in-process analytical database that runs SQL over DataFrames.
- **pandera**: a schema/validation library that formalizes dataframe checks.

## Self-check (quiz)

Open [`quiz.md`](quiz.md) and answer all 10 questions. The passing bar is **8/10**; each question names the Concepts subsection or notebook cell it comes from.

## Exercises

Four graded exercises, **Easy** (run the cleaning notebook and record the counts), **Standard** (document the five planted issues with evidence), **Stretch** (rewrite the on-time query with a window function and assert agreement), and **Portfolio** (turn cleaning into a runnable `make_silver.py`). Hints for each live in [`exercises.md`](exercises.md).

## Sources

- pandas user guide (missing data, merge/groupby): https://pandas.pydata.org/docs/user_guide/index.html
- pandas `groupby` documentation: https://pandas.pydata.org/docs/user_guide/groupby.html
- DuckDB SQL documentation: https://duckdb.org/docs/sql/introduction
- DuckDB Python API: https://duckdb.org/docs/api/python/overview
- DuckDB window functions: https://duckdb.org/docs/sql/window_functions
- pandera documentation: https://pandera.readthedocs.io/
- Andrew Ng, *The AI Engineering Skills Map*, The Batch issue 366: https://www.deeplearning.ai/the-batch/issue-366
- Fereydun Hashemi (Zorost), *The AI Engineering Skills Map, turned into a training plan*: https://zorost.com/ai-engineering-skills-map-training-guide
- Aurélien Géron, *Hands-On Machine Learning*, 3rd ed. (O'Reilly, 2022): https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/
