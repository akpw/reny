# Reny
Reny is a lightweight but powerful filesystem visualizer, batch renamer and
organization CLI tool. It visualizes complex directory structures and generates virtual
views, alongside handling standard renaming tasks (regex replace, padding, appending
text/dates) and advanced operations like multi-level indexing and folder flattening. By
default, Reny safely visualizes all targeted changes and requires confirmation before
modifying the filesystem.

![demo](https://github.com/user-attachments/assets/5a69f2d7-839b-4707-8b29-054dbca915d8)

## Background
`reny` was originally created as the `renamer` component inside the larger [`batchmp`](https://github.com/akpw/batch-mp-tools) suite. It was spun off to provide a pure-filesystem organizing tool without media dependencies. 

## Blogs
 - [The Next Chapter in File Organization: Introducing Reny](https://akpw.github.io/articles/2026/08/06/Reny-Organize-and-More.html)

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
- *Virtual Views*: Preview how a directory structure would look when reorganised by type or date without moving or changing anything
- *Organization*: Safely re-organizes directory structure based on type or date attributes
- *Git Integration*: Automatically detects and displays file and directory modification statuses using `--git` (`-g`), filters to show only modified files (`-go`), tracked files (`-gt`), untracked files (`-ngt`), or explicitly ignored files (`-gi`).
- *Dry-Run by Default*: `reny` always visualizes targeted changes and asks for confirmation before actually touching files / folders
- *Indexing*: Multi-level indexing across nested directories, supporting multiple indexing schemes
- *Padding*: Automatically pad existing numbers in filenames with leading zeros to fix sorting orders
- *Flattening*: Safely collapse nested directory structures into a single folder
- *Regex Replacement*: Powerful batch renaming using standard regular expressions
- *Directory Statistics*: Fast summary of total files, directories, and disk space usage
- *Flexible CLI Parsing*: Position-independent options that work before or after subcommands

## Commands Summary

| Command | Description | Example |
|---|---|---|
| `print` | Visualize directory tree structure (default) | `reny -el 2` |
| `stats` | Overall file & directory count and size statistics | `reny stats` |
| `index` | Numeric indexing (sequential or directory-scoped) | `reny index -sf 1 -md 2` |
| `pad` | Pad numbers with leading zeros | `reny pad -md 3` |
| `add_date` | Add formatted date timestamp as prefix or suffix | `reny add_date -ap -fm '%Y-%m-%d'` |
| `add_text` | Add arbitrary text as prefix or suffix | `reny add_text -ap -tx 'archived_'` |
| `remove` | Remove N characters from filename head or tail | `reny remove -nc 3 -ft` |
| `replace` | Regex find-and-replace with expandable templates | `reny replace -fs ' ' -rs '_'` |
| `capitalize` | Capitalize words in file and folder names | `reny capitalize` |
| `flatten` | Collapse directory hierarchy below target depth | `reny flatten -tl 1` |
| `organize` | Organize files into subdirectories by type or date | `reny organize -b type` |
| `delete` | Batch delete matching files and folders safely | `reny -gi delete -id` |
| `config` | Generate or edit local or global `config.toml` | `reny config --local` |
| `ignore` | Generate or edit `.renyignore` template file | `reny ignore` |
| `version` / `info` | Display version information or overview | `reny version` |

> [!TIP]
> **Flexible Argument Order**: Global flags (`-d`, `-r`, `-el`, `-ex`, `-in`, `-q`, `-g`, `-s`) can be placed either before or after subcommands (e.g., `reny pad -d ./photos -md 3` and `reny -d ./photos pad -md 3` are equivalent).

## Usage & Examples

### Configuration File
Since `reny` comes with many options, it supports setting default configurations via a TOML file to make organizing and using them much easier. 

The global configuration file is located at `~/.config/reny/config.toml`, but you can also use a local `./.reny.toml` on a per-directory basis.

Generate a fully-commented default configuration template (or open an existing one in your `$EDITOR`):
```bash
reny config            # Generates or opens ~/.config/reny/config.toml
reny config --local    # Generates or opens ./.reny.toml in current directory
```

Any options specified on the command line automatically override settings in the config file.

### Ignore Files
`reny` supports generating and managing ignore template files to exclude unwanted files or directories from operations:

```bash
reny ignore            # Generates or opens ./.renyignore in current directory
reny ignore -gl        # Generates or opens ~/.renyignore globally
```

### Directory Tree Visualization
Print the current directory structure:
```bash
reny
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md
  |-/reny
  |-/tests
3 files, 2 folders
```

### Recursion Depth
Adjust how deep `reny` prints or operates using `-el` / `--end-level` and `-sl` / `--start-level`. For example, to view files and directories exactly 1 level deep:
```bash
reny -el 1
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md
  |->/reny
    |-/cli
    |-/commons
    |-/fstools
  |->/tests
    |-/base
    |-/commons
    |-/fs
3 files, 8 folders
```

### Pattern & File Filtering
By default, `reny` automatically excludes hidden files and directories (like `.git` and `.venv`). Additional filters can be set via `-in` / `-ex` parameters, or via a `.renyignore` file in the target directory or globally in `~/.renyignore`. `reny` also supports custom ignore files, like a standard `.gitignore`:
```bash
reny -el 1 -ig .gitignore 
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md 
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
5 files, 8 folders
```

### Virtual Views & Organization
Preview how a chaotic downloads folder would look if organized by file type, sorted by size descending (you can also sort by date with `da`/`dd`), without actually moving anything:
```bash
reny -b type -s sd -ss
```
```text
Virtual view by type:
~/Downloads
  |->/mp4
    |-  1.2GB vacation_movie.mp4
  |->/mov
    |-  450MB screen_recording.mov
  |->/pdf
    |-  2.1MB tax_return.pdf
    |-  450KB receipt.pdf
  |->/png
    |-  1.2MB screenshot.png
5 files, 4 folders
Total selected entries size: 1.6GB
```
To commit this organization and move files into subdirectories, use `organize`. `reny` will show a preview and ask for confirmation before making changes:
```bash
reny organize -b type
```

### Git Status Integration
Visually inspect changes in a repository using `--git` (`-g`). `reny` automatically bubbles up file modifications to parent directories:
```bash
reny -el 1 -ig .gitignore --git
```
```text
/../_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md [ M]
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
5 files, 8 folders
```

To exclusively view files with git modifications (and their parent directories), hiding all unmodified clutter (similar to `git status`), use the `--git-only` (or `-go`) flag:
```bash
reny -el 1 -ig .gitignore -go
```
```text
/../_Dev/reny
  |- README.md [ M]
  |->/reny [* ]
    |-/cli [* ]
1 file, 2 folders
```

Similarly, `--git-tracked` (`-gt`) filters the view to show only tracked files, `--not-git-tracked` (`-ngt`) displays only untracked files, and `--git-ignored` (`-gi`) reveals all explicitly ignored files (bypassing `.renyignore`).

### Directory Statistics
Quickly calculate total file count, directory count, and total disk usage across matching paths:
```bash
reny stats
```
```text
Overall directory statistics might take a while...
/../_Dev/reny
  Total files: 4
  Total directores: 17
  Total size: 22.4MB
```
You can combine `stats` with any filter or recursion depth (e.g. `reny -el 2 -in '*.py' stats`).

### Batch Renaming Operations
When modifying files, `reny` operates purely as a dry-run by default. It safely visualizes all targeted changes and asks for confirmation before any files are moved or renamed.

#### Numeric Indexing (`index`)

Add an index to all `.txt` files recursively. By default, `reny` performs multi-level indexing (restarting the count inside each respective directory):
```bash
reny -r -in '*.txt' index
```
To index files continuously across all nested directories, use `-sq`. Alternatively, use `-bd` to append the directory's index instead of the file's index:
```bash
reny -r -in '*.txt' index -sq
```

#### Zero-Padding (`pad`)

Pad existing numbers with leading zeros (e.g., `2.png` becomes `02.png`):
```bash
reny pad -md 2
```

#### Date Timestamps (`add_date`)

Add a formatted date timestamp to filenames as a prefix or suffix:
```bash
# Prepend current date (YYYY-MM-DD_) to all JPEG images
reny -in '*.jpg' add_date -ap -fm '%Y-%m-%d'

# Append date as suffix using custom join string
reny -in '*.log' add_date -fm '%Y%m%d' -js '_'
```

#### Text Insertion (`add_text`)

Add arbitrary text as a prefix or suffix:
```bash
# Prepend 'archived_' to all PDF files
reny -in '*.pdf' add_text -ap -tx 'archived'
```

#### Character Removal (`remove`)

Strip N characters from the beginning or end of filenames:
```bash
# Remove first 4 characters from filenames
reny remove -nc 4

# Remove last 3 characters from filename tails (preserves extension)
reny remove -nc 3 -ft
```

#### Word Capitalization (`capitalize`)

Automatically capitalize words in selected file and folder names:
```bash
reny capitalize
```

#### Folder Flattening (`flatten`)

Safely collapse nested directory structures into a single folder (target level 1):
```bash
reny flatten -tl 1
```

#### Batch Deletion (`delete`)

Safely batch-delete files. When combined with filters, it can clean up temporary files or build artifacts. Paired with `-gi`, you can preview and wipe all git-ignored files:
```bash
reny -gi -ex .venv delete -id
```
```text
The following files / folders will be deleted
/reny
  |-  6KB .DS_Store
  |->/ 3.4MB .mypy_cache
    |-  0KB .gitignore
    |-  0KB CACHEDIR.TAG
    |-/ 3.4MB 3.14
  |->/ 5KB .pytest_cache
    |-  0KB .gitignore
    |-  0KB CACHEDIR.TAG
    |-  0KB README.md
  |->/ 103KB dist
    |-  56KB reny-1.1.0-py3-none-any.whl
    |-  47KB reny-1.1.0.tar.gz
  |->/ 13KB reny.egg-info
    |-  0KB dependency_links.txt
    |-  0KB entry_points.txt
    |-  11KB PKG-INFO
    |-  0KB requires.txt
    |-  1KB SOURCES.txt
    |-  0KB top_level.txt
14 files, 5 folders
Total selected entries size: 3.5MB
```

#### Regex Replace (`replace`)

Change spaces to underscores in all filenames:
```bash
reny replace -fs ' ' -rs '_'
```
Manually pad single-digit filenames with a leading zero (using capture groups):
```bash
reny replace -fs '^(\d)$' -rs '0\1'
```
Delete the first 3 characters from every filename:
```bash
reny replace -fs '^.{1,3}' -rs ''
```

## Documentation
For a deep dive:
- [The Next Chapter in File Organization: Introducing Reny](https://akpw.github.io/articles/2026/08/06/Reny-Organize-and-More.html)

While `reny` is standalone, its core logic inherits from `batchmp`. You can find historical context and tutorials in the original blog posts:
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
