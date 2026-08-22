# Writing

How this project writes prose, for humans and agents alike. It governs
`README.md`, notebook prose (`mo.md()` cells and module docstrings), commit
messages, docstrings, and source comments — every surface a reader reaches.

For environment setup, the gates, and pull request workflow, see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Voice

Three surfaces, one voice. A docstring says what a function or class
guarantees; a notebook's `mo.md()` prose says what the reader is looking at;
a source comment says why the code does something non-obvious. All three are
present tense, lead with the thing being described, and stop. Why something
was built that way belongs in the commit message, which is timestamped and
attached to the diff.

The most useful editing operation is deleting the introductory sentence.

Lead with verbs and name concrete things. Put identifiers in backticks.
Prefer short declarative sentences, one operational fact each. Do not explain
Python to Python developers; do explain this project's semantics.

Type annotations describe shape. Documentation describes meaning. A sentence
that restates a signature has said nothing.

Use MUST, SHOULD, and MAY only where the normative sense is meant. Say what
actually happens rather than that something is "supported".

| Instead of                       | Prefer                            |
| --------------------------------- | ---------------------------------- |
| "We added…"                      | "`curriculum.py` now accepts…"    |
| "New and improved"               | "The drift gate now…"             |
| "powerful", "seamless"           | state the capability              |
| "easily", "simply", "just"       | omit                              |
| "simple", "obvious", "intuitive" | omit                              |
| "robust"                         | name the failure that is handled  |
| "comprehensive"                  | name what is covered              |
| "production-ready"               | state the guarantee               |
| "optimized", "blazingly fast"    | give the magnitude                |
| "various fixes"                  | name the components               |
| "under the hood"                 | omit unless observable            |
| "please note that", "note that"  | state the fact                    |
| "leverage", "utilize"            | "use"                             |
| "delve into"                     | "read", or omit                   |
| "best practices"                 | name the practice                 |
| "in order to"                    | "to"                              |

## Who you are writing for

The default reader is fluent in Python and new to this repository. They can
read a `groupby` call; they cannot guess what `--sandbox` does, what a rung
is, or why a notebook has no shared environment. Serve them first.

A second, smaller reader extends the curriculum engine
(`scripts/curriculum.py`) or authors new notebooks. Serve them too, but mark
their material opt-in — "for the rarer cases", "advanced" — so the default
reader, here to study a library rather than maintain the repo, knows they can
stop.

Rules that follow:

- **Second person, present tense, active.** "You open the notebook", not "A
  notebook is opened". Address the reader who is doing the thing.
- **Concept before mechanics.** Open by saying what a notebook teaches, or
  what a function does, before its signature or its cell code. The signature
  is the last detail a reader needs, not the first.
- **Say when they can stop.** Lead with the default and the reassurance. Let
  a skimmer leave after one paragraph.
- **Grant permission, do not demand attention.** "Reach for this when…" tells
  readers they are in the right place without implying they must read on.
- **Progressive disclosure.** Order by how many readers need it: the common
  call, then the one argument a few will tune, then the lower-level
  primitive. Each step is for a smaller audience than the last.
- **Name the trade-off.** If something costs something — an isolated
  environment's slower first run, a disk cache that survives a restart but
  can go stale — say so, and say what it buys. State it; do not sell it.

## README

A README is the shortest path from "what is this?" to competent use, not the
project's autobiography.

The first sentence is a contract. It says what the reader has been handed,
concretely enough to tell this repository apart from a plain Jupyter project.

Get to a runnable command before anything the reader can skip. A logo, a
mission statement, and three paragraphs of history in front of the first
command all cost the same thing.

State the minimum Python version and meaningful platform constraints in
prose. `requires-python` in `pyproject.toml` is the authority; the README
must agree with it.

Examples show a real command, a real path, and a real flag — never
`your-command <some-options>`. See
[Documented examples that run](#documented-examples-that-run) for which
blocks this repository executes today, and how to write one that would
qualify if that ever changes.

Document the semantic model, not the flag list. `--help` and `just --list`
already enumerate commands; what they cannot say is what a notebook expects
to already exist, what goes to stdout versus a browser tab, and what a
non-zero exit means.

State defaults explicitly — defaults are API. State negative guarantees
where they exist: "no shared runtime environment", "no network access
required to browse the gallery". They establish boundaries faster than any
amount of description.

Headings stay conventional and stable, because people deep-link them.
Badges, if any are ever added, should be few and load-bearing.

## Notebook prose and output

Every notebook is a marimo `.py` file, not a Jupyter `.ipynb` — there is no
cell-output JSON embedded in the file. Output is computed fresh on every run
and never serialized into source; `__marimo__/`, marimo's per-notebook cache
and snapshot directory, is gitignored. Nothing about a run's output is
committed.

Teaching prose lives in `mo.md()` cells and follows [Voice](#voice) the same
as any other prose in this project. Give every teaching section a markdown
heading (`##` or deeper) in a plain `mo.md()` cell — marimo's Outline panel
builds its navigation from headings in rendered markdown, and headings
inside `mo.accordion`, `mo.ui.tabs`, or `mo.carousel` do not appear there.

A notebook's module docstring is plain human prose — one line naming the
library and topic, no track or rung code. A notebook's place in the
curriculum (`track`, `rung`, `project`) is authored in
`notes/curriculum.toml`, not in the docstring. See
[notebooks/AGENTS.md](../notebooks/AGENTS.md) for the rest of the
marimo-specific authoring rules.

Notebooks execute in CI, but only a curated subset: the smoke-run step in
`.github/workflows/ci.yml` runs each lightweight notebook headlessly
(`uv run <notebook>.py`). Notebooks with heavy dependencies or model
downloads are deliberately excluded — see "CI-safety" in
[notebooks/AGENTS.md](../notebooks/AGENTS.md).

## Documented examples that run

Pytest collects no doctests in this repository today. There is no
`[tool.pytest.ini_options]` table in `pyproject.toml` — no
`--doctest-modules` or `--doctest-glob` addopt, no `doctest_optionflags`, and
no `testpaths` entry pointing at `README.md` or `notes/`. `tests/conftest.py`
only adds `scripts/` to `sys.path` so the tests can `import curriculum`; it
defines no `doctest_namespace` fixture. A `>>> ` prompt in a docstring or a
Markdown file is prose today, not a test: nothing collects or runs it, and
none currently appear in the repository.

The repository's executable documentation takes a different shape: a marimo
cell named `test_*` inside a notebook is pytest-discoverable
(`uv run --with pytest pytest notebooks/<domain>/<library>/NNN_topic.py`),
and its asserts also run whenever the notebook executes headlessly — which is
what the CI smoke-run step does for the lightweight notebooks it lists.

If a doctest mechanism is ever adopted here — a `testpaths` entry, doctest
addopts, a `doctest_namespace` fixture — this section is where the fence tag,
the prompt convention, and the enabled option flags get documented.

## Docstrings

The prime directive: never restate the type. The annotation is the source of
truth; the docstring carries what the annotation cannot.

This is documentation debt wearing a docstring:

    def primary_track(notebook: Notebook, tracks: list[Track]) -> Track | None:
        """Get the notebook's primary track.

        Parameters
        ----------
        notebook : Notebook
            The notebook.
        tracks : list[Track]
            The tracks.

        Returns
        -------
        Track | None
            The track.
        """

Document instead the dimensions the type system cannot encode:

- **Mutation.** What it changes in place.
- **Ownership.** What the caller must close, release, or keep alive.
- **Ordering.** Whether results come back in a guaranteed order.
- **Failure.** Which exceptions are raised and what triggers each.
- **Idempotence.** Whether calling twice does anything the second time.
- **Units and ranges.** What a number means and what values are accepted.
- **Boundary behaviour.** What zero, empty, and the maximum do.
- **Platform.** Behaviour that differs by operating system or dependency
  version.

The first sentence stands alone; tooling truncates there. PEP 257 applies:
triple double quotes, an imperative one-line summary ending in a period, a
blank line before any extended description. Do not repeat an introspectable
signature.

One docstring dialect per repository, enforced by the linter rather than
relitigated in review: `ruff`'s `pydocstyle` rules run with `convention =
"numpy"`. That linting is scoped — `notebooks/**/*.py` and
`notes/notebook_template.py` disable the `D` rules (docstring rules do not
fit marimo's generated cell functions), and so does `tests/**/*.py` (test
names are the documentation there).

**Classes with fields** — `NamedTuple`, dataclasses — document every field in
an `Attributes` section:

```python
@dataclass
class Concept:
    """A teaching concept joining notebooks, sources, and projects.

    Attributes
    ----------
    id : str
        Slug the curriculum file keys the concept by.
    gloss : str
        One-line prose describing the concept.
    """
```

A type says how a field is shaped, not what it holds. Describing each one
keeps that meaning next to the code, and anything that renders the class —
autodoc, a REPL, an editor tooltip — has a description to show instead of a
bare name.

## Source comments

A comment ships only if it passes all three gates. Fail any: delete or
rewrite. Borderline: delete — borderline means the information is
reconstructible, which is what makes deletion cheap.

**Loss.** Three years from now, would losing this cost a maintainer real time
rediscovering intent, an invariant, a constraint, or a failure mode the code
and tests do not already make obvious?

**Elite.** Would SQLite, Redis, the Go standard library, or CPython write
this comment, at this length? Those projects state the constraint and stop.
They do not argue with an imagined objector.

**Upkeep.** Will it stay true without maintenance? A comment that hand-syncs
a value the code owns — a count, an offset, a line reference, a duplicated
constant — is false the first time that value moves.

### Ceiling

One or two lines. A comment reaching four is either carrying several facts,
in which case split it, or arguing, in which case cut it to the fact.

Rationale, alternatives weighed, and the story of how the code got here
belong in the commit message: timestamped, attached to the exact diff, and
free to maintain.

A comment often holds both a constraint and the deliberation that found it.
Keep the constraint, cut the deliberation. "Runs at most once per second"
survives; "this is the right trade for now" does not.

### Keep

- Why over how: upstream quirks, protocol and compatibility constraints,
  performance tradeoffs still part of the contract.
- Invariants, preconditions, ordering, lifetime, and concurrency
  requirements that types and tests cannot express.
- Code that looks wrong but is not, so a later cleanup does not reintroduce
  the bug.
- A high-level sketch of an algorithm whose local operations do not reveal
  the whole.

### Delete

- Narration of the next lines; code translated into English.
- Restated names, types, defaults, or control flow.
- Values duplicated from the code and hand-synced.
- Justification, hedging, or apology for a choice.
- Speculation about future requirements.
- History version control already holds, including commented-out code.
- Ticket and issue numbers. They say nothing to a reader without tracker
  access, and they rot when the tracker moves. Unfinished work goes in the
  tracker, not the source.
- Transient observations — "currently", "for now", "the latest release" —
  that go stale with no nearby edit.

### The upkeep gate in practice

It reaches values that track our own code. It does not reach frozen external
facts.

Bad (Delete):

```python
# There are 321 tests to complete for servers.
```

Good (Keep):

```python
# CPython < 3.11 has no ExceptionGroup, so this branch stays.
```

### Documentation exception

Minimal usage examples, and parameter, return, and raises entries on public
API, are exempt from the loss gate — they serve the caller, not the
maintainer. They are exempt from nothing else. Ceiling: a good man page
entry. NumPy-style `Parameters`, `Returns`, and `Attributes` sections fall
under this exception — autodoc ships every field whether or not you describe
it.

## Terminology and capitalization

Pick the domain noun and keep it: a **track** is a course, a **rung** is its
worded mastery level, a **project** is a studied library's registry entry, a
**concept** is a cross-reference slug. Do not call a track a course in one
paragraph and a track in the next.

Stable vocabulary is what makes search, deep links, and an agent's retrieval
work at all.

Python and PyPI keep their own capitalisation. Distribution names are
written as they are published.

Do not write counts into prose — how many notebooks exist, how many tracks
there are. They go stale silently and no reader needs them. Counts that pin
a fixture or guard an invariant are different, and belong in code.

## Markdown

Prose wraps at 80 columns. Table rows, badge lines, and long links are
exempt, because breaking them harms rendering. A pull request or issue body
does not wrap at all: GitHub renders a single newline as a space in a file
and as a line break in a comment, so a wrapped comment body arrives as
ragged stubs.

GitHub alert blocks — `> [!NOTE]`, `> [!WARNING]` — render as literal text
outside GitHub, so reserve them for at most one load-bearing warning per
document. Write the sentence so it carries the fact on its own, and a
renderer that drops the marker loses nothing.

Do not use a local absolute path or an email address in anything published.

## Code blocks

Code blocks are paste-and-run units: pasting one block runs exactly one
intended action.

- **One command per block.** Multiple steps may share a block only when
  explicitly chained with `&&`, `;`, or `\` continuations — the chain is
  then one logical command.
- **Explanations go in prose above the block**, never as `#` comments inside
  it.
- **Command menus are per-command blocks with prose lead-ins**, not tables.
- **Shell commands use the `console` tag with a `$ ` prefix.** This
  separates interactive commands from scripts and enables prompt-aware copy.
- **Split long commands with `\`** — one flag or flag+value pair per
  indented continuation line, positional arguments last.

Good — show the last ten commits as a graph:

```console
$ git log \
    --max-count=10 \
    --graph \
    --oneline
```

Bad:

```console
# Show the last ten commits as a graph
$ git log --max-count=10 --graph --oneline
```

## Commits

```
Scope(type[detail]): concise description

why: Explanation of necessity or impact.

what:
- Specific technical changes made
- Focused on a single topic
```

Keep the subject to 50 characters or fewer, excluding any trailing `(#NN)`
pull request reference, and wrap body lines at 72. Separate the `why:` and
`what:` blocks with a blank line, or leave them adjacent when the `why:` is
one short line.

Routine maintenance commits drop the colon and take a capitalised
description, which is what distinguishes them at a glance in `git log
--oneline`:

```
py(deps[dev]) Bump dev packages
ai(rules[AGENTS]) Judge comments by three gates
```

Everything that changes behaviour keeps the colon.

Common types:

- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev dependencies
- **ai(rules[AGENTS])**: AI rule updates
- **ai(claude[rules])**: Claude Code rules (`CLAUDE.md`)

Subjects are plain English. Never put taxonomy codes (`A1`, `C3`, `L2`) or
other repo-internal shorthand in the subject line — a reader of `git log
--oneline` should understand every title cold. Taxonomy references belong in
the body, spelled out (e.g. "fills the languages-and-runtimes row in
`notes/taxonomy.md`").

Example:

```
polars(feat[lazy]): Inspect query plans before collecting

why: Show the optimizer's predicate pushdown so readers stop guessing
what .explain() output means.

what:
- Add notebooks/data/polars/001_lazy_frames.py from the template
- Register the notebook in the CI smoke-run list
- Link the notebook from its taxonomy row
```

For a multi-line message, use a heredoc so the formatting survives:

```console
$ git commit -m "$(cat <<'EOF'
Scope(feat[detail]): Concise description

why: Explanation of the change.

what:
- First change
- Second change
EOF
)"
```

## Slop prevention

Treat AI slop as review-hostile noise, not as proof that text or code is
wrong. The goal is to maximise information density.

- **AI signatures.** No "Generated by", no conversational filler, no
  unexplained emoji, no tool metadata.
- **Brittle references.** No hard-coded line numbers, fragile file or test
  counts, dated "as of" claims, or bare SHAs — unless they are strict
  evidentiary artefacts such as a benchmark log. Local absolute paths are
  never permitted, evidentiary or not.
- **Diff narration.** Do not restate what moved, was renamed, or was removed
  in anything the reader holds alongside the diff: code, docstrings, README,
  or a pull request description. The diff and the commit message already
  carry it.
- **Branch-internal narrative.** Do not mention intermediate states,
  abandoned approaches, or "no longer" behaviour unless users of a published
  release actually experienced the old state — see The Published-Release
  Test below.
- **Low-value scaffolding.** No ownerless TODOs, unused future-proofing,
  debug artefacts, or defensive wrappers around failure modes nothing can
  reach.
- **Prose inflation.** The diction table under [Voice](#voice) governs;
  replace an inflated word with a concrete description of behaviour,
  constraints, or trade-offs.
- **Coded labels.** Write rules and findings as plain imperatives. No
  `[R1]`, `Option B`, or any index a reader has to decode.

Preserve the "why". Never delete a comment documenting an invariant, a
protocol constraint, a platform quirk, or an upstream workaround — those are
the facts [Source comments](#source-comments) keeps, and every other comment
is judged by it.

### Durable source links

Link to a pinned revision, never to trunk. A pinned permalink is not a
brittle reference; an unlinked SHA dropped into prose is. `blob/master/…`
links rot silently — the file moves, lines shift, and the anchor lands on
unrelated code while still resolving. This is exactly what
`notes/sources.jsonl` exists to get right for every notebook's upstream
citations.

- Prefer a release tag (`blob/v1.4.0/…`). Most durable, and it tells the
  reader which released version the claim held for.
- Otherwise use a 7-char commit ref (`blob/9a29b1a/…`) reachable from trunk.
  Never a PR-head SHA — it can be rebased or garbage-collected.
- Reserve `blob/master/…` for living documents meant to always show the
  latest state, such as a contributing guide.
- Line anchors (`#L120-L145`) are only safe on a pinned ref.
- A notebook's source-reading cell names the upstream GitHub URL, never a
  machine-relative clone path (`../../rust-python/polars`) — that leaks a
  local layout and means nothing downstream.

### The Published-Release Test

Long-running branches accumulate tactical decisions — renames, refactors,
attempts-then-reverts. When deciding what counts as branch-internal, use
trunk as the baseline, not an intermediate state inside the current branch.
Ask:

> Did users of the most recently published release ever experience this old
> name, old behaviour, or bug?

If the answer is no, it is branch-internal narrative. Move it to the commit
message and describe only the final state in the artefact.

### Cleanup in hindsight

When applying these rules retroactively from inside a feature branch, first
establish scope by diffing against trunk to identify which commits the
branch actually introduced.

- **In-branch commits:** either `fixup!` commits with `git rebase
  --autosquash` to address each causal commit at its source, or a single
  cleanup commit at branch tip.
- **Trunk commits:** leave them alone unless the change is explicitly
  requested; fold any such cleanup into a single commit at branch tip rather
  than rewriting shared history.
- **Scope guard:** if cleaning prior slop would touch a colleague's work or
  expand the branch beyond its stated goal, leave prior slop alone.
