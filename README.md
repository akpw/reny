# Reny
Reny is a lightweight but powerful filesystem visualizer, batch renamer and
organization CLI tool. It visualizes complex directory structures and generates virtual
views, alongside handling standard renaming tasks (regex replace, padding, appending
text/dates) and advanced operations like multi-level indexing and folder flattening. By
default, Reny safely visualizes all targeted changes and requires confirmation before
modifying the filesystem.

## Background
`reny` was originally created as the `renamer` component inside the larger [`batchmp`](https://github.com/akpw/batch-mp-tools) suite. It was spun off to provide a pure-filesystem organizing tool without media dependencies. 

## Installation
Homebrew:
```bash
brew tap akpw/tap
brew install reny
```

Alternatively, install from the [PyPI package](https://pypi.org/project/reny) using standard `pip`:
```bash
pip install reny
```

Or for a clean `pip` installation with isolated dependencies via [pipx](https://pypa.github.io/pipx/):
```bash
pipx install reny
```

## Features
- *Filesystem Visualization*: Clean, customizable views of files and folders
- *Recursion & Leveling*: Precise recursion control with `end_level` / `start_level` parameters
- *Filtering*: Pinpoint targeting using include/exclude patterns and `.renyignore` integration
- *Color Outputs*: Rich terminal highlighting for different file types, grouping extensions visually
- *Virtual Views*: Preview how a directory structure would look when reorganised by type, size, or date without moving or changing anything
- *Git Integration*: Automatically detects and displays file and directory modification statuses using `--git`
- *Dry-Run by Default*: `reny` always visualizes targeted changes and asks for confirmation before actually touching files / folders
- *Indexing*: Multi-level indexing across nested directories, supporting multiple indexing schemes
- *Padding*: Automatically pad existing numbers in filenames with leading zeros to fix sorting orders
- *Flattening*: Safely collapse nested directory structures into a single folder
- *Regex Replacement*: Powerful batch renaming using standard regular expressions

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

### 2. Recursion Control (`-r`/`--recursive`, `-sl`/`--start-level`, `-el`/`--end-level`)
Easily adjust how deep `reny` prints or operates. For example, to view files and directories exactly 1 level deep:
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

### 3. Filtering & Ignore Files (`-in`/`--include`, `-ex`/`--exclude`, `-ig`/`--ignore-file`)
By default, `reny` automatically excludes hidden files and directories (like `.git` and `.venv`). Additional filters can be set via `-in` / `-ex` parameters, or via a `.renyignore` file in the target directory or globally in `~/.renyignore`. `reny` also supports custom ignore files, like a standard `.gitignore`:
```bash
reny -el 1 -ig .gitignore 
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md 
  |- setup.py
  |->/reny
    |- __init__.py
    |-/cli
    |-/commons
    |-/fstools
  |->/tests
    |- __init__.py
    |-/base
    |-/commons
    |-/fs
6 files, 8 folders
```

### 4. Virtual Views & Organization (`-b`/`--by`, `-ss`/`--show-size`, `-s`/`--sort`)
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
To actually commit this organization and move the files, simply use the `organize` command. As always, `reny` will show a preview and ask for confirmation before actually making any changes:
```bash
reny organize -b type
```

### 5. Git Integration (`--git`)
Visually inspect changes in a repository. `reny` automatically bubbles up file modifications to their parent directories.
```bash
reny -el 1 -ig .gitignore --git
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md [ M]
  |- setup.py
  |->/reny [* ]
    |- __init__.py
    |-/cli [* ]
    |-/commons
    |-/fstools
  |->/tests
    |- __init__.py
    |-/base
    |-/commons
    |-/fs
6 files, 8 folders
```

### 6. Advanced Batch Renaming (Commands)
When you are ready to modify your files, `reny` operates purely as a dry-run by default. It safely visualizes all targeted changes and asks for confirmation before any files are moved or renamed.

`reny` supports a variety of targeted commands for bulk renaming:

**Indexing (`index`, `-sq`/`--sequential`, `-bd`/`--by-directory`)**

Add an index to all `.txt` files recursively. By default, `reny` performs multi-level indexing (restarting the count inside each respective directory):
```bash
reny -r -in '*.txt' index
```
To index files continuously across all nested directories, use the `-sq` flag. Alternatively, use `-bd` to append the directory's index instead of the file's index:
```bash
reny -r -in '*.txt' index -sq
```

**Zero-Padding (`pad`, `-md`/`--min-digits`)**

Pad existing numbers with leading zeros (e.g., `2.png` becomes `02.png`):
```bash
reny pad -md 2
```

**Flattening (`flatten`, `-tl`/`--target-level`)**

Safely collapse nested directory structures into a single folder (target level 1):
```bash
reny flatten -tl 1
```

**Regex Replace (`replace`, `-fs`/`--find-string`, `-rs`/`--replace-string`)**

Change spaces to underscores in all filenames:
```bash
reny replace -fs ' ' -rs '_'
```
Manually pad single-digit filenames with a leading zero (an alternative to the `pad` command using capture groups):
```bash
reny replace -fs '^(\d)$' -rs '0\1'
```
Delete the first 3 characters from every filename:
```bash
reny replace -fs '^.{1,3}' -rs ''
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
