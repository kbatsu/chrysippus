# Releasing chrysippus

Maintainer-only checklist for cutting a release.

## Versioning

- This project follows [Semantic Versioning 2.0.0](https://semver.org/).
- A change to a persona's lexicon or non-breaking flavor addition is a **minor**
  bump.
- A breaking change to a skill's frontmatter, removal of a flavor, or rename of
  a persona is a **major** bump.
- A typo fix, doc update, or generator-internal refactor is a **patch** bump.

## Pre-release checklist

1. **All CI green** on `main`.
2. **CHANGELOG.md** has an entry for the new version under
   `## [<version>] — <YYYY-MM-DD>`. Move items from `## [Unreleased]`.
3. **Generated files in sync** — run locally:
   ```bash
   scripts/render.sh
   scripts/check.sh
   ```
   No drift.
4. **Tests pass locally**:
   ```bash
   tests/run.sh
   ```
5. **Plugin manifest version bumped**:
   ```bash
   jq '.version = "<version>"' .claude-plugin/plugin.json > .tmp && mv .tmp .claude-plugin/plugin.json
   ```
6. **Eval suite passing** (manual trigger of `evals.yml` workflow on `main`).
7. **`PLAN.md` reviewed** — anything completed since last release moved to
   "shipped" notes or removed if absorbed into normal docs.

## Cutting the release

```bash
# 1. Final commit with version bump + CHANGELOG
git add CHANGELOG.md .claude-plugin/plugin.json
git commit -m "chore: release v<version>"

# 2. Annotated, signed tag
git tag -s -a v<version> -m "v<version>"

# 3. Push
git push origin main
git push origin v<version>

# 4. CI release.yml fires on the tag — builds tarball, computes SHA256,
#    creates GitHub Release with notes from CHANGELOG.

# 5. Verify the release artifacts
gh release view v<version>
```

## Post-release

- **Marketplace.json** — update `.claude-plugin/marketplace.json` to pin the
  plugin entry to the new tag (or `main` if intentionally tracking head).
- **Announce** — open a GitHub Discussion under the "Releases" category with
  the CHANGELOG entry and any migration notes.
- **Reset `## [Unreleased]`** — add a fresh empty section to CHANGELOG so the
  next change has somewhere to land.

## Hotfix process

1. Branch from the release tag: `git checkout -b hotfix/v<x.y.z+1> v<x.y.z>`.
2. Apply the fix; bump patch version.
3. Tag, push, create release as above.
4. Cherry-pick the fix back to `main`.

## Yanking a release

If a release contains a critical issue (security, data loss, broken hook):

1. Mark the GitHub Release as "Pre-release" + add a banner in the release notes
   directing users to the next safe version.
2. Open a `SECURITY.md`-style advisory if it's a vulnerability.
3. Cut a hotfix release ASAP.
4. Do **not** delete the tag — that breaks downstream installs.
