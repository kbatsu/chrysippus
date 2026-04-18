# Evals

Harness for evaluating persona skill output against per-persona rubrics.

**Status**: scaffold only. Rubrics are defined in `rubrics/`; the runner
that actually calls the Claude API to generate and grade outputs is a
deferred follow-up (tracked in `CHANGELOG.md` under the `v1.0.0` release
notes / deferred-follow-ups list).

## What evals are for

Evals verify that each persona's rendered skill produces output that:

1. **Matches the register** — required style markers present (e.g.,
   thou/thee for shakespeare, "mans" for toronto-mans).
2. **Honours preservation** — backtick contents, commits, safety warnings,
   etc. stay in plain English per the config.
3. **Hits flavor-specific traits** — e.g., shakespeare's `sonnet` flavor
   produces a rhymed iambic couplet on completion; pirate's `shanty`
   produces a 4-line trochaic shanty.
4. **Stays within guardrails** — excluded vocabulary does not appear;
   attribution is correct; stereotype-drift rules are honoured.
5. **Respects safety yields** — destructive-op confirmations, security
   warnings render in plain English.

## Layout

```
evals/
├── README.md            ← you are here
├── rubrics/
│   ├── shakespeare.yml
│   ├── pirate.yml
│   ├── gen-alpha.yml
│   └── toronto-mans.yml
├── prompts/             ← (not yet present) fixed prompt corpus
└── runs/                ← (not yet present; .gitignored) output from each run
```

## Running evals (future)

When the runner is implemented:

```bash
evals/run.py --persona shakespeare --flavor sonnet
evals/run.py --all                        # all personas, all flavors
evals/run.py --budget 5.00                # dollar ceiling for API spend
```

Runs are cost-gated — they use the Claude API as judge and generator, so
they don't run on every PR. The `evals.yml` workflow (to be added) runs
on release branches and weekly cron.

## Contributing a rubric

Each rubric in `rubrics/<persona>.yml` declares:

- **`required_tokens`** — at least one must appear per response
  (register marker — thou/thee, arr/avast, etc.).
- **`forbidden_tokens`** — must never appear (excluded lexicon).
- **`preservation_checks`** — patterns that must be preserved verbatim
  (backtick contents, specific error lines, etc.).
- **`flavor_specific`** — per-flavor requirements (e.g., sonnet couplet
  structure, shanty line count).

See existing rubric files for examples.
