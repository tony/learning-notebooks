# learning-notebooks tasks — thin wrappers over uv/marimo. Every recipe body
# is a plain shell command you can run yourself (see AGENTS.md). Notebook
# arguments are real paths, so your shell tab-completes them by domain:
#   just edit notebooks/data/<TAB>

# Bare `just` lists everything below.
default:
    @just --list

# tree of notebooks by domain
[group('notebooks')]
list:
    @fd -e py . notebooks/ | sort

# edit a notebook — prints the URL, does NOT open a browser
[group('notebooks')]
edit nb *args:
    uv run marimo edit --sandbox --headless {{ nb }} {{ args }}

# edit a notebook and open the browser
[group('notebooks')]
open nb *args:
    uv run marimo edit --sandbox {{ nb }} {{ args }}

# run a notebook headlessly as a script (its PEP 723 deps resolve in a sandbox)
[group('notebooks')]
run nb:
    uv run {{ nb }}

# serve a notebook as a read-only app — prints the URL, no browser
[group('notebooks')]
serve nb *args:
    uv run marimo run --sandbox --headless {{ nb }} {{ args }}

# fuzzy-pick a notebook with fzf, then edit it (no browser)
[group('notebooks')]
pick:
    @just edit "$(fd -e py . notebooks/ | fzf)"

# browse all notebooks in marimo's directory gallery (browse-only — sandboxed deps need `just edit`)
[group('notebooks')]
gallery:
    uv run marimo edit --headless notebooks/

# scaffold notebooks/<domain>/<library>/001_<topic>.py from the template
[group('notebooks')]
new domain library topic:
    mkdir -p notebooks/{{ domain }}/{{ library }}
    cp notes/notebook_template.py notebooks/{{ domain }}/{{ library }}/001_{{ topic }}.py
    @echo "created notebooks/{{ domain }}/{{ library }}/001_{{ topic }}.py — now: just edit notebooks/{{ domain }}/{{ library }}/001_{{ topic }}.py"

# regenerate notes/taxonomy.md from notebooks + notes/curriculum.toml
[group('curriculum')]
sync:
    uv run scripts/curriculum.py render

# drift gate: fail when generated files or curriculum metadata are stale
[group('curriculum')]
drift:
    uv run scripts/curriculum.py check

# all quality gates (what CI runs)
[group('quality')]
check:
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check
    uv run marimo check --strict notebooks/ notes/notebook_template.py
    uv run scripts/check_licenses.py
    uv run scripts/curriculum.py check

# format the repo
[group('quality')]
fmt:
    uv run ruff format .
