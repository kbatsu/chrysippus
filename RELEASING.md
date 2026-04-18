# Releasing chrysippus

Maintainer-only checklist for cutting a release.

Release notes are sourced from the **annotated tag message** plus the commit
log since the previous tag — there is no `CHANGELOG.md`. Write substantive
tag messages.

## Versioning

- This project follows [Semantic Versioning 2.0.0](https://semver.org/).
- A change to a persona's lexicon or non-breaking flavor addition is a **minor**
  bump.
- A breaking change to a skill's frontmatter, removal of a flavor, or rename of
  a persona is a **major** bump.
- A typo fix, doc update, or generator-internal refactor is a **patch** bump.

## Pre-release checklist

1. **All CI green** on `main`.
2. **Generated files in sync** — run locally:

   ```bash
   scripts/render.py
   scripts/render.py --check
   ```

   No drift.

3. **Tests pass locally**:

   ```bash
   scripts/ci.sh
   ```

4. **Plugin manifest version bumped** to the new `<version>` in both
   `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.

5. **Eval suite passing** (manual trigger of `evals.yml` workflow on
   `main`) — once the eval runner exists.

## Cutting the release

```bash
# 1. Final commit with version bump
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore: release v<version>"

# 2. Annotated, signed tag with substantive release notes
git tag -s -a v<version> -m "v<version>

  <one-paragraph summary of what shipped>

  <bullet list of major changes — these become the GitHub Release body>"

# 3. Push
git push origin main
git push origin v<version>

# 4. CI release.yml fires on the tag — builds tarball, computes SHA256,
#    creates GitHub Release. The release body is the tag annotation
#    followed by `git log` between the previous tag and this one.

# 5. Verify the release artifacts
gh release view v<version>
```

## Post-release

- **Marketplace.json** — confirm `.claude-plugin/marketplace.json` is on
  the new tag (or `main` if intentionally tracking head).
- **Announce** — open a GitHub Discussion under "Releases" with a
  summary of major changes, drawn from the tag message.

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
