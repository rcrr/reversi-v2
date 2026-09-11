# Decisions log — historical record

Format: D-NNN | date | decision | rationale

This is the append-only HISTORICAL LOG: the "why" of every action
and commit in this workspace. It grows without bound and is
consulted only when needed or for historical research. The rules
in force right now live in notes/rules.md (the active
legislation): when a decision establishes an enduring rule, the
rule is promoted there with this D-number as the origin pointer
(same commit); a retirement removes the line from rules.md and
is logged here with a new D-number. D-numbers are sequential and
never reused or renumbered (the docs' State lines and the
cross-references depend on them). Volumes (D-118): the open log
keeps this name (notes/decisions.md); when it exceeds 2000
lines it closes at a session boundary as notes/decisions_NNN.md
and a new open log is opened — the D-numbers stay global across
volumes (volume 000: D-001…D-116, closed 2026-09-06; volume 001:
D-117…D-158, closed 2026-09-11).

D-159 | 2026-09-11 | I-017 T2 executed: the PRNG port — the
        64-bit MT-19937 in the new core module reversi/
        feature_prng.py, line-by-line from Roberto's C
        (scratch/prng.c, 2017). Scoping: the full MT family
        (the 15 prng_mt19937_* functions) ported; the 4
        prng_stdlib_* wrappers + the clock-based seed skipped
        (the stdlib wrappers are a no-sense in Python; the
        clock seed is non-deterministic and unused — the
        pipeline seed comes from the config and is part of the
        cache signature). DESIGN RULING (Roberto, overriding
        Nia's pure-Python proposal): NUMPY, strict types —
        every 64-bit value in the data path is np.uint64 (the
        type itself applies the C unsigned-wraparound contract:
        no unbounded Python ints, no manual masking; the
        machine is 64-bit, the bitboard is 64-bit, and the
        numba era is the substrate argument); the by-design
        wraps are silenced with a local errstate; loop counters
        stay plain ints (control flow, not data). The C quirks
        kept verbatim: the init_by_seed multiplier
        6364136223846793005 (NOT the 32-bit-reference
        6364136293807784493) and the mti == nn after init (the
        first get_uint64 twists the just-initialized array).
        The 3 bitw_* helpers inlined in extract_from_set64
        (the popcount, (s-1)&s, the de Bruijn bsf) — no
        separate bit_works module (the port is the prng only).
        Verification: the T2 bit-exact cross-check vs the C
        build (prng.c + bit_works.c + time_utils.c + the
        disposable harness in scratch/): 64 seed-42 + 64
        init-by-array uint64, 8 doubles, 16 choices — ALL
        MATCH in warnings-as-errors mode; the 10-test smoke
        micro-suite (the determinism, the dtype pins, the no-
        consume contracts k==1 / n<=1, the extract semantics;
        the two first failures were test-side mistakes — the
        state inspected after the draws, the advanced
        instance — caught and fixed); default 781/0/94 + LONG
        781/0/21 GREEN; the hub probe ALL PASS (the pipeline is
        untouched — the port is purely additive). The bit-exact
        GOLDEN suite (the committed sequences + the published
        vectors + the 100k equi-distribution) is the T3
        (test_feature_prng.py extended). Also in the wave: the
        I-018 idea recorded (the top-20 outlier report in
        VALIDATE + the records in the context — Roberto's
        2026-09-11 ask, the D-150 report relocation; Nia's
        opinion: agreed on both points).
