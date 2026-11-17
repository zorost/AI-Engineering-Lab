# Week 01: Quiz (10 questions, 8/10 to pass)

Answer all ten, then check against the answer key. A question marked *(see Concepts §X)* points at a README subsection; *(see notebook cell Y)* points at a cell in `01-environment-and-tools.ipynb` or `02-zorologistics-data-generator.ipynb`.

1. **Multiple choice.** Which of the following *correctly* names the four skills in Andrew Ng's AI Engineering Skills Map? *(see Concepts §1)*
   a. Prompt engineering, fine-tuning, RAG, deployment
   *b. Building/deploying AI applications, software engineering fundamentals, using coding agents, shaping the build*
   c. Data engineering, ML, deep learning, MLOps
   d. Frontend, backend, data, DevOps

2. **Multiple choice.** Why does `shipments(100_000, seed=42)` return 100,200 rows instead of 100,000? *(see Concepts §6, notebook "Verify persistence" cell)*
   a. A rounding error in NumPy
   *b. The generator plants ~0.2% duplicate rows on purpose for Week 2 to find*
   c. The seed only applies to carriers, not shipments
   d. `save_all()` always adds 200 header rows

3. **Short answer.** In the seed cell, `first_five(42)` returns `[89250, 773956, 654571, 438878, 433015]` on its first call. What does it return on the *second* call with the same seed, and why? *(see notebook "seed habit" cell)*
Same result, because we used the same seed

4. **Multiple choice.** What is the modern, recommended NumPy form for seeded randomness, and why is it preferred over the legacy global form? *(see Concepts §6)*
   *a. `np.random.seed(42)`, simpler and thread-safe*
   b. `numpy.random.default_rng(seed)`, local and thread-safe, no hidden global state
   c. `random.random(42)`, built-in and faster
   d. `np.random.RandomState`, deprecated but required

5. **Short answer.** The environment notebook's final cell computes `READINESS = CHECK_PYTHON + CHECK_LIBS + CHECK_ZORO + CHECK_GIT + CHECK_NUMPY + CHECK_SEED`. What does a score of 6 mean, and what should you do if it is 5? *(see notebook final cell)*
6 = 6 x True

6. **Multiple choice.** In `zoro/data.py`, which column is a *foreign key* into the `lanes` table? *(see Concepts §2, data dictionary)*
   a. `shipments.shipment_id`
   *b. `shipments.lane_id`*
   c. `lanes.lane_id`
   d. `carriers.carrier_name`

7. **Multiple choice.** The generator notebook resolves the output directory by walking up to the folder containing `zoro/` before calling `save_all(...)`. What failure does this prevent? *(see notebook "Generate and persist" cell)*
   *a. Writing `data/` into the *notebook folder* instead of the repo root*
   b. A seed collision between carriers and lanes
   c. Duplicate `shipment_id` values
   d. A Git merge conflict in `data-dictionary.md`

8. **Short answer.** Name the three data-quality flaws planted in the Week 1 output, and give the approximate count of each under seed 42. *(see Concepts §6, verification cell)*
Duplicate data

9. **Multiple choice.** The data dictionary in `02-zorologistics-data-generator.ipynb` writes `data/data-dictionary.md` from a list of tuples. What four fields does each tuple carry? *(see notebook "data dictionary" cell)*
   *a. table, column, dtype, meaning*
   b. table, seed, dtype, count
   c. column, value, sample, note
   d. name, type, nulls, source

10. **Short answer.** Why is the same seed a *contract* ("same seed, same company") for the whole program, rather than just a convenience? *(see Concepts §6 and the Friday Zorost gate)*
Reproducible results

## Answer key

1. **b.** Ng's four areas are building/deploying AI applications, software engineering fundamentals, using coding agents, and shaping the build. Prompt engineering and RAG are building blocks *within* area one, not the four areas themselves.

2. **b.** `data.py` runs `pd.concat([df, df.sample(frac=0.002)])` to plant ~0.2% duplicate rows (200 of 100,000) so Week 2 has a real cleaning task.

3. **The identical list** `[89250, 773956, 654571, 438878, 433015]`. A fixed seed makes `default_rng` replay the same sequence; only a different seed (e.g. `7`) produces different numbers.

4. **b.** `numpy.random.default_rng(seed)` returns a local generator object, so no hidden global state can be re-ordered by other library calls. `np.random.seed` mutates global state and can silently break reproducibility.

5. **6 means all six checks passed** (Python version, imports, `zoro.data` completeness, Git, NumPy, determinism) and the environment is ready. At 5, read each FAIL line, fix the one broken check, and re-run until it is 6, do not continue on a failing environment.

6. **b.** `shipments.lane_id` references `lanes.lane_id`; `shipment_id` is the shipments table's own primary key, not a foreign key.

7. **a.** Without resolving to the repo root, `save_all()` would write relative to the kernel's cwd, often the notebook folder, so the CSVs would land in the wrong place and break every later week's `data/` paths.

8. **Duplicate shipment rows (~200, from a 0.2% sample), `NaN` `weight_kg` values (~301, from a 0.3% sample), and `NaN` `lane.distance_km` (~1, from a 5% sample of 20 lanes).** All three are planted so Week 2 has something to find.

9. **a.** Each tuple is `(table, column, dtype, meaning)`; the notebook builds a DataFrame from these and then writes the Markdown table.

10. **A seed lets any stranger re-run your fork and get byte-identical data**, so a metric measured in Week 23 on "the same" dataset is comparable to Week 1's baseline. Determinism is what turns an anecdote into a reproducible artifact; without it, later weeks' comparisons are meaningless.
