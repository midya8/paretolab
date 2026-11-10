# ParetoLab

**The compromise a weighted sum misses.** An inspectable finite biobjective AI-planning laboratory with full path enumeration, exact support intervals, every optimizer tie and a separately checked dynamic-program label trace.

Three synthetic alternatives cost `(0,12)`, `(7,7)` and `(12,0)`. None dominates another. But for the middle path to minimize `t*x + (1-t)*y`, it needs both `t >= 7/12` and `t <= 5/12`. No weight works. Constrain the second cost to at most7 instead and that path wins.

Allow a random choice of a whole path under an *expected* ceiling and the answer changes: choose the first extreme with probability7/12 and the other with probability5/12 for expected costs `(5,7)`. The first extreme still violates the realized ceiling with probability7/12. Expected feasibility is not a hard-bound guarantee.

## Run

Python3.10+, no runtime dependencies:

```sh
python -m paretolab demo > certificate.json
python -m paretolab verify certificate.json
python -m paretolab run input.json
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/` for the browser lab. Everything runs locally. No API, account, telemetry or external assets are required. The page links to papers but does not fetch them during analysis.

Installable console entrypoint:

```sh
python -m pip install .
paretolab demo
```

## What is inspectable

- Every start-to-goal path, edge sequence, two-cost vector and strict dominator.
- All equal-vector path identities, not one arbitrary representative.
- The complete intersection of each path's pairwise scalarization inequalities, exact rational endpoints and constant contradictions.
- Every point/open-interval optimizer cell on `t in [0,1]`, including zero-weight dominated ties.
- Every attained epsilon threshold plus one infeasible threshold, lexicographic deterministic minimizers and all equal-vector ties.
- All optimal basic one-/two-path expected-cost mixtures, exact probabilities and realized-ceiling violation probability. This is not every distribution in an optimal face.
- A reverse-node Pareto-label dynamic program with each local candidate, its dominators and kept suffixes; a separate exhaustive suffix count remains visible.
- Editable strict JSON, source/report downloads and stale-evidence clearing on edit or rejection.

## Model and terminology

2–7 ordered nodes, <=12 forward arcs, two additive nonnegative integer minimization costs0..20, <=64 suffix paths per node. Start0, goal`n-1`. Parallel edges are valid and identify different paths. A disconnected graph is valid and reports no feasible optimum.

Here **positive-weight supported** means optimal for some `0 < t < 1`. **Closed support** separately includes `t=0,1`; a dominated path can be an endpoint minimizer, but never becomes Pareto. Nondominated collinear interior points count as supported even if optimal only at one interior weight. Other literature sometimes uses different supportedness conventions.

Costs use supplied units, without automatic normalization. Scaling an objective changes weight breakpoints. See [MODEL.md](MODEL.md) for exact contracts and proofs of the finite reductions.

## Verification

```sh
python tools/check_assets.py
python -m unittest discover -s tests -v
python tools/check_installed.py
node --test tests/test_engine.cjs tests/test_browser.cjs
python -m pip install scipy==1.15.3
python tools/check_reference.py
```

Chrome and Node22 are needed for the browser test. Set `CHROME_BIN` if Chrome is not on the default path. SciPy is used only by the optional numeric reference, not the producer, independent checker or lab.

The Python checker imports input validation only. It independently enumerates forward paths, sweeps every objective-line intersection and reconstructs label/mixture evidence. The browser replay changes traversal but shares evidence construction. Shared theory, input schema and canonical tie conventions can share mistakes; agreement is not formal verification.

See [EVIDENCE.md](EVIDENCE.md) for executed test coverage, scope and reproduction. [SOURCES.md](SOURCES.md) credits established theory and existing software.

## Limits and publication state

This is classical finite multiobjective planning, not a new algorithm, learned agent, discounted MDP, routing service, real-world cost estimator or scale benchmark. A whole-path lottery is not a per-step randomized control policy. The tool cannot validate supplied costs or provide safety guarantees. Synthetic controls illustrate mechanisms, not prevalence or measured practical advantage.

Local implementation, independent checks and responsive browser inspection are documented here. Public source, CI, deployment and showcase status must be verified separately against the exact current commit; a source file or a successful local run alone is not a deployment-completion claim.

MIT licensed.
