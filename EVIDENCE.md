# Executed local evidence

Run date: November10,2026. Development fixtures are synthetic and supplied, not observed user or customer data. No paid service or external model was used.

| Check | Executed result |
|---|---|
| Native unit suite |20 passing Python tests |
| Exhaustive small profiles |729 ordered three-parallel-path profiles over all9 cost vectors in0..2 |
| Full native/browser parity |52 reports,101 paths,176 point/open weight cells,130 epsilon thresholds |
| Primitive-field forgeries |579 independently rejected mutations per engine, across default and label-pruning controls |
| Installed reproduction |Wheel outside source;6 site-package module origins;12 controls;2 entrypoints;24 CLI forgery rejections |
| Numerical reference |SciPy1.15.3 HiGHS;556 graph-MILP/probability-LP solves;2,403 constraint rows; maximum observed objective error8.881784197001252e-16, tolerance1e-8 |
| Actual Chrome behavior |48 control/width views;220 path selections;208 weight cells;180 budget states;324 local label candidate rows |
| Native browser downloads |24 files; every certificate independently replayed with Python |
| Local visual evidence |40 unmasked captures; desktop/mobile atlas, hard-versus-expected budget and320px label-pruning pixels inspected |

The exhaustive729-profile test independently verifies every report, checks that the epsilon sweep recovers exactly the frontier, and checks supported paths are nondominated. It is a bounded exhaustive result, not coverage of every7-node input or evidence of performance.

Python tests also cover collinear three-way ties, dominated endpoint minimizers, equal-vector path identities, all-zero costs, no feasible path, actual label pruning, strict field/JSON/type rejection,64-path acceptance/81-path rejection, no input mutation or report aliasing, parallel-edge identity permutation, positive scaling and exact weight reparametrization, atlas score recomputation, mixture probability/cost/violation reconstruction and CLI fail-closed behavior.

The two primitive-forgery sets modify every scalar leaf once: numbers increment, booleans flip, null becomes zero and strings receive an invalid suffix. This includes the embedded source input, so the checker must recompute all dependent evidence. Separate shape tests change arrays, fields, types and rational spelling. This is not a security proof or exhaustive adversarial fuzzing.

The numeric reference uses binary edge flows constructed from original input arcs, not a serialized feasible-path matrix. It solves each weight-cell witness and every deterministic epsilon objective, with a second solve for the lexicographic tie objective. Its probability LP independently optimizes over the enumerated full paths and re-solves second-cost ties. It checks objective values and feasibility, not every tie, label, interval or report field. All disagreement assertions are hard failures; numerical failures are never relabeled as infeasible unless HiGHS reports infeasible.

Chrome checks full reports, pairwise inequality rows, complete atlas/epsilon ledgers, every budget's exact mixture rows and every node's label rows. It checks responsive overflow at1440,768,390,320px. Real pointer events trigger completed input/report downloads, not merely Blob construction. Exported JSON is compared byte-content semantically to native reports and its certificate is replayed by the separate Python checker. Invalid edits immediately remove old evidence and disable both exports; rejection remains cleared.

## Reproduce

```sh
python tools/check_assets.py
python -m unittest discover -s tests -v
python tools/check_installed.py
node --test tests/test_engine.cjs tests/test_browser.cjs
python -m pip install scipy==1.15.3
python tools/check_reference.py
```

`python tools/make_cases.py` regenerates the committed synthetic cases. A clean asset check compares them against fresh native reports. The seed fixes developed coverage; it does not make those40 DAGs independent empirical samples. Twelve hand-specified controls expose the intended corner cases. No search for a practical speed advantage was performed.

## Publication gate

Local checks passed. Public source/CI/Pages byte fidelity, deployed behavior and portfolio/profile showcase inspection are separate completion gates against the exact published commit. This local-evidence document alone is not a public-deployment completion report.
