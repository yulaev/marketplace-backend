---
name: formatted-commit
description: Splits pending/staged changes in this repository into narrow, logically-grouped commits and writes messages matching this repo's own git history style. Use whenever asked to commit changes, create commits, or "commit this" in this repo — not just when explicitly invoked by name.
---

## Core rule: the commit unit is the logical change, not the file

Group files that only make sense together into one commit (e.g. a schema change plus the crud code that consumes it, or a model change plus its migration). Do not default to "one file, one commit" — that is not the goal and is explicitly discouraged.

The one hard constraint is the reverse: **never split a single file's diff across two commits.** No `git add -p`, no interactive patch/hunk staging, no `git stash` tricks to engineer a partial commit of one file. If a file happens to contain two unrelated logical threads, commit that file whole, once — accept the impurity rather than fragmenting it.

Consequences:
- Tightly-coupled multi-file changes → one commit.
- A file with two unrelated changes tangled together → still one commit for that whole file.
- Never use `git add -A` or `git add .` — always stage explicit paths (`git add path/to/file ...`) so each commit's contents are deliberate.

## Unrelated changes always get their own commit(s)

Anything not part of the task at hand — a `.gitignore` tweak, a dependency bump, an unrelated config edit found sitting in the working tree — is split into its own commit(s), separate from the actual feature/fix/test work, regardless of how small it is.

## No size-based fallback

Even when a batch touches many files, keep splitting strictly by logical change. Do not switch to "group by directory/feature" just because the file or commit count is high — a larger number of small, narrow commits is preferred over coarser grouping.

## Commit order

When creating several commits in one batch, order them by dependency, foundational-first:

1. Schema / model changes
2. Crud / business logic that consumes them
3. Routers / API layer
4. Tests exercising the above
5. Unrelated changes (config, `.gitignore`, dependency bumps, docs) last

## Message style: mimic this repo's own history

Before writing any commit message, run something like `git log --oneline -20` on the target repo and match its actual observed style — capitalization, punctuation, whether it uses conventional-commit prefixes (`feat:`, `fix:`) or plain descriptive sentences, single-line vs. multi-line body. Do not impose an external convention (e.g. Conventional Commits) if the repo doesn't already use one. Re-check this per repo/session rather than assuming a previously-seen style still applies.

Do not add attribution/co-author lines unless the session's attribution configuration calls for them — that's controlled separately and shouldn't be hardcoded here.

## Test gate

Run the full test suite once, after the whole commit batch has been made (not before every individual commit), and surface any failures rather than treating the batch as done.

## Standard git safety (reiterated for this workflow)

- Never `git commit --amend` an existing commit unless explicitly asked.
- Never force-push.
- Never skip hooks (`--no-verify`, etc.) to get a commit through.
- This skill governs *how to split, order, and word* commits — it does not replace or bypass any project rule that commits require human review before they happen (e.g. a `PreToolUse` hook that gates `git commit`). That gate still applies to every commit this skill produces.

## Worked example

Given a batch that: (1) requires a schema field to become non-optional, (2) requires a crud function to reject an invalid state, (3) adds/extends a test file for feature A, (4) adds one test to an unrelated test file for feature B, (5) adds new project config files, and (6) bumps a dependency in `requirements.txt` — the correct split is six commits, in this order:

1. `<schema file>` — the schema fix
2. `<crud file>` — the crud fix
3. `<test file A>` — full file, one commit, even though it covers many different test cases across several endpoints
4. `<test file B>` — the one new test
5. `<new config files>` — grouped together as one logical addition
6. `requirements.txt` — the dependency bump, last, unrelated to everything else

Each commit message is a short line matching the repo's existing `git log` tone (e.g. `Restock quantity is now required`, `Reject deleting a seller user that still has active listings`, `Finished product route tests`) — no prefixes, no body, unless the repo's own history shows otherwise.
