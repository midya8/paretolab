# Exact finite model

## Inputs and identities

`{"version":1,"nodes":2,"edges":[{"from":0,"to":1,"cost":[0,12]},{"from":0,"to":1,"cost":[7,7]},{"from":0,"to":1,"cost":[12,0]}]}`

All object fields are exact. Booleans, JSON decimals/exponents, duplicate JSON fields, extra fields, invalid node order and exceeded bounds are rejected. Python's parser rejects decimal tokens; native Python API validation rejects float values. Browser JSON parsing has a64KiB byte limit. CLI input limit is64KiB; certificate limit8MiB. These are resource limits, not complexity or memory guarantees.

There are2..7 nodes,0..12 arcs, costs0..20. Every edge satisfies `0 <= from < to < nodes`. Each node has at most64 complete suffixes to the goal, counted by a reverse-node integer DP before enumerating paths. This bounds dead/unreachable-to-source suffix work too, not just source paths. An81-path four-stage parallel graph is rejected; a64-path12-arc input is accepted. Node IDs are topological order, not learned spatial coordinates.

A path starts at0 and ends at`nodes-1`, with edge IDs being input positions. Lexicographic edge sequences define canonical full path IDs. Equal-cost paths keep distinct IDs. The goal has one empty suffix; a source disconnected from the goal has zero complete paths.

## Dominance and label DP

For minimization, vector`a` strictly dominates`b` when every component is no larger and at least one is smaller. Equality is not dominance. The frontier consists of every path not strictly dominated by any other path.

For each node in reverse order, extend each retained child suffix by its outgoing edge, then discard strictly dominated candidate vectors. Equal-vector candidates remain. If suffix`u` dominates suffix`v`, then `prefix+u` dominates`prefix+v` because both receive the same additive prefix. Thus discarding a dominated suffix cannot delete a nondominated complete path. This argument does not assume that an arbitrary scalar cost summarizes every tradeoff.

The trace's local candidate set omits extensions of already-pruned child suffixes. `full_suffix_count` counts all complete suffixes, including those. The separate complete path census, not the local label trace, proves the reported path list is exhaustive within the supplied DAG.

## Exact weighted-sum support

For path`z=(x,y)` versus path`w=(u,v)`:

`(x-u-y+v)*t <= v-y`.

Positive coefficients impose upper bounds; negative coefficients impose lower bounds; a zero coefficient with negative right-hand side is a constant contradiction. Intersect all inequalities with `[0,1]`, using exact reduced rationals.

`closed_support` is nonempty intersection. `positive_support` additionally intersects`(0,1)`. A singleton at an interior weight counts, including a collinear interior frontier point. A singleton at0 or1 is endpoint-only, not positive support. Dominated paths may tie at endpoints, because a zero-weight objective is ignored. `supported` lists positive-supported paths; `unsupported` lists frontier paths lacking positive support. It does not list all paths without support, because many are dominated instead.

The atlas splits `[0,1]` at every closed-support endpoint. Every breakpoint is its own point cell; intervals between breakpoints are open cells. Optimizer identities are constant inside each open cell. A rational midpoint witnesses its score and minimizers. This is not a finite weight grid used to infer untested support.

Raw objective units are used. Positive rescaling of either objective preserves support existence by reparametrizing the positive weights, but changes breakpoint values. There is no automatic normalization or conversion from ordinal preferences.

## Epsilon constraints

For each attained second cost, minimize first cost among paths satisfying`cost2 <= epsilon`, then minimize second cost among primary minimizers. Keep every equal-vector minimizing path. A primary-only tie could otherwise include a dominated path. Include one threshold below the smallest attained second cost, which must be infeasible. When there are no paths, a single threshold0 is infeasible.

Every deterministic Pareto vector is selected at its own second-cost threshold: a feasible path with lower first cost would dominate it, and an equal first/lower second path would also dominate it. Thus the union of lexicographic minimizers over these finite thresholds is exactly the full deterministic frontier. This does not claim an arbitrary coarse epsilon grid is complete.

## Expected-bound lotteries

Choose a complete path once, with probabilities`p_i >= 0`, `sum(p)=1`. Bound `sum(p_i*y_i) <= epsilon`, lexicographically minimize expected first then second cost. This differs from requiring the second cost of each realized path to be at most epsilon.

An extreme point of a probability simplex intersected with one inequality has either one positive probability, or two positive probabilities with the inequality binding. With three or more positive probabilities, the sum and binding-budget equalities have a nonzero feasible perturbation preserving both; the point is not extreme. Without a binding budget, any two-positive vector is not extreme. Hence enumerating all feasible singletons and strictly positive two-support intersections suffices to find the lexicographic optimum.

The report keeps every optimal basic witness in that enumeration. A continuum of distributions can mix optimal vertices; it does not enumerate that continuum or claim that every optimal lottery is a listed basic witness. Equal-cost different paths can produce distinct singleton vertices. Pair witnesses at probability0/1 are represented only by the corresponding singleton to avoid duplicates.

`violation_probability` sums probability on paths whose realized second cost strictly exceeds that threshold. Expected feasibility may have positive violation probability. It is not a safety certificate, risk constraint, chance constraint or risk-sensitive objective.

## Replay and numeric limits

The producer uses reverse suffix construction and pairwise half-line clipping. The Python verifier imports only strict input validation, enumerates forward paths independently, builds the complete arrangement of all objective-line crossings, then classifies support from its cells. Local candidates are rebuilt from independently classified complete suffixes. Mixture probabilities use a separate2x2 determinant formula. Full canonical report comparison checks all arrays, types, rational spelling and unexpected fields, so arbitrary alternative witnesses are not accepted by this format.

Browser replay independently changes path traversal but shares the browser evidence builder. It is deliberately not called an independent checker. Python uses arbitrary-precision integer/Fraction operations; browser rationals use checked safe-integer numerators/denominators. The finite input bounds keep all objective operations safely below2^53. Numeric reference checks are floating-point, tolerance1e-8; they cannot certify exact ties or replace canonical replay.

Nothing here proves that an input describes real costs, that a graph captures a planning environment, or that a lottery is acceptable for a user's constraints.
