# Reny
A lightweight but powerful filesystem visualizer, batch renamer and organization CLI tool.

## Background
`reny` was originally created as the `renamer` component inside the larger [`batchmp`](https://github.com/akpw/batch-mp-tools) suite. It was spun off to provide a pure-filesystem organizing tool without media dependencies. If you want a modern alternative to `ls` or `eza` that doesn't just visualize your file trees, but actually lets you re-organize and modify them with surgical precision, `reny` is all you need.

## Installation
You can install `reny` directly from the [PyPI package](https://pypi.org/project/reny) using standard `pip`:
```bash
pip install reny
```

Alternatively, for a cleaner global installation that isolates dependencies, use [pipx](https://pypa.github.io/pipx/):
```bash
pipx install reny
```

## Features
- **Filesystem Visualization:** Clean, customizable views of files and folders
- **Recursion & Leveling:** Precise recursion control with `end_level` / `start_level` parameters
- **Filtering:** Pinpoint targeting using include/exclude patterns and `.renyignore` integration
- **Color Outputs:** Rich terminal highlighting for different file types, grouping extensions visually
- **Virtual Views:** Preview how a directory structure would look when reorganised by type, size, or date without moving or changing anything
- **Git Integration:** Automatically detects and displays file and directory modification statuses using `--git`
- **Dry-Run by Default:** `reny` always visualizes targeted changes and ask for confirmation before it actually touching files / folders
- **Indexing:** Multi-level indexing across nested directories, supporting multiple indexing schemes
- **Padding:** Automatically pad existing numbers in filenames with leading zeros to fix sorting orders
- **Flattening:** Safely collapse nested directory structures into a single folder
- **Regex Replacement:** Powerful batch renaming using standard regular expressions

## Usage & Examples

### 1. Basic Visualization
Print the current directory structure:
```bash
reny
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md
  |- setup.py
  |-/reny
  |-/tests
4 files, 2 folders
```

### 2. Recursion Control (`-r`, `-sl`, `-el`)
Limit how deep `reny` prints or operates. For example, to view only directories exactly 1 levels deep:
```bash
reny -el 1
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md
  |- setup.py
  |->/reny
    |-/cli
    |-/commons
    |-/fstools
  |->/tests
    |-/base
    |-/commons
    |-/fs
4 files, 8 folders
```

### 3. Filtering & Ignore Files (`-in`, `-ex`, `-ig`)
By default, `reny` automatically excludes hidden files and directories (like `.git` and `.venv`). It will also automatically detect and apply any `.renyignore` files found in your target directory (or globally in `~/.renyignore`) to cleanly exclude specific paths.

If you are working inside a repository, you can explicitly pass a custom ignore file, like your standard `.gitignore`, to automatically parse and exclude those paths from the output:
```bash
reny -ig .gitignore
```
```text
~/Projects/app
  |- main.py
  |->/src
    |- utils.py
    |- database.py
3 files, 1 folder
```
*(Notice that `__pycache__` and `.venv` are cleanly omitted).*

### 4. Virtual Views & Organization (`-b`, `-ss`, `-s`)
Preview how a chaotic downloads folder would look if organized by file type, sorted by size descending, without actually moving anything:
```bash
reny -b type -s sd -ss
```
```text
Virtual view by type:
~/Downloads
  |->/video
    |- vacation_movie.mp4 (1.2 GB)
    |- screen_recording.mov (450 MB)
  |->/document
    |- tax_return.pdf (2.1 MB)
    |- receipt.pdf (450 KB)
  |->/image
    |- screenshot.png (1.2 MB)
5 files, 3 folders
```
To actually commit this organization and move the files, simply use the `organize` command:
```bash
reny organize -b type
```

### 5. Git Integration (`--git`)
Visually inspect changes in a repository. `reny` automatically bubbles up file modifications to their parent directories.
```bash
reny --git
```
```text
~/Projects/repo
  |-[* ] main.py
  |->[* ]/src
    |-[* ] utils.py
    |- database.py
```

### 6. Advanced Batch Renaming (Commands)
When you are ready to modify your files, `reny` operates purely as a dry-run by default. It safely visualizes all targeted changes and asks for confirmation before any files are moved or renamed.

`reny` supports a variety of targeted commands for bulk renaming:

**Regex Replace (`replace`)**
Change spaces to underscores in all filenames:
```bash
reny replace -fs ' ' -rs '_'
```

**Sequential Indexing (`index`)**
Add a sequential index to all `.txt` files recursively:
```bash
reny -r -in '*.txt' index
```

**Zero-Padding (`pad`)**
Pad existing numbers with leading zeros (e.g., `2.png` becomes `02.png`):
```bash
reny pad -md 2
```

**Flattening (`flatten`)**
Safely collapse nested directory structures into a single folder:
```bash
reny flatten
```

## Documentation
Although `reny` is standalone, its core logic inherits from `batchmp`. You can find detailed tutorials in the original blog posts:
- [Renamer Organize & Virtual Views](https://akpw.github.io/articles/2025/09/22/Print-and-Organize.html)
- [BatchMP Tools Tutorial](https://akpw.github.io/articles/2015/04/11/batchmp-tutorial-part-ii.html)

## Development
1. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com/akpw/reny.git
   cd reny
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the project in editable mode along with testing dependencies:
   ```bash
   pip install -e ".[test]"
   ```

## Running Tests
To run the full test suite (which dynamically creates and cleans up temporary sandboxes):
```bash
pytest -v --tb=short tests/
```
