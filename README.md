# Reny
A lightweight, fast, and safe batch renaming and filesystem organization tool.

## Background
`reny` was originally created as the `renamer` component inside the larger [`batchmp`](https://github.com/akpw/batch-mp-tools) (Batch Media Processing) suite. It was spun off into its own standalone package to provide for an ultra-lightweight, safe, pure-filesystem organizing tool without FFmpeg / Mutagen media dependencies. 

If you need advanced media operations (like denoising, cover-art extraction, or format transcoding), check out the original [`batchmp`](https://github.com/akpw/batch-mp-tools) project. If you just need to safely organize your files with surgical precision, `reny` is all you need.

## Installation
You can safely install `reny` from the [PyPI package](https://pypi.org/project/reny) using [pipx](https://pypa.github.io/pipx/):
```bash
pipx install reny
```
*(Note: If this is your first time using `pipx`, you may need to run `pipx ensurepath` once to ensure the installed tools are available in your terminal).*

## Features
- **Dry-Run by Default:** `reny` will always visualize targeted changes and ask for confirmation before it ever touches your files 
- **Virtual Views:** Preview how a directory structure would look when reorganised by type, size, or date without moving or changing anything
- **Filtering & Leveling:** Precise targeting using include/exclude patterns and recursion control with 'end_level` / `start_level` parameters
- **Indexing:** Multi-level indexing across nested directories, supporting multiple indexing schemes
- **Padding:** Automatically pad existing numbers in filenames with leading zeros to fix sorting orders
- **Flattening:** Safely collapse nested directory structures into a single folder
- **Regex Replacement:** Powerful batch renaming using standard regular expressions

## Examples

### Basic Operations
**Print current directory structure:**
```bash
reny
```
*(Without arguments, `reny` defaults to the `print` command)*

**Add a sequential index to all `.txt` files recursively:**
```bash
reny -r -in '*.txt' index
```

**Limit Recursion Depth (`-el`):**
Use `-el` (end level) to control exactly how deep `reny` recurses. For example, to add an index only to files inside immediate subdirectories (depth 1), while ignoring deeper nested folders:
```bash
reny -r -el 1 index
```

**Pad existing numbers with leading zeros (e.g., `2 kms.png` becomes `02 kms.png`):**
```bash
reny pad -md 2
```

**Regex Replace:**
Change spaces to underscores in all filenames:
```bash
reny replace -fs ' ' -rs '_'
```

### Advanced Operations & Virtual Views
**Flattening nested directories:**
Collapse all sub-directories and bring their files up to the current folder level:
```bash
reny flatten
```

**Organize by File Type:**
Move files into sub-directories grouped by their file extension (e.g., `png/`, `pdf/`):
```bash
reny organize -b type
```

**Virtual Views (Dry-Run Preview):**
Preview how files would look if organized by year and month, *without actually moving any files on your drive*:
```bash
reny print -b date --date-format "%Y/%m"
```
```text
Virtual view by date:
~/Downloads
  |- 2025/
    |- 01/
      |- document.pdf
    |- 02/
      |- image.png
```

### Ignore Files (.renyignore)
By default, `reny` will automatically detect a `.renyignore` file in your target directory (falling back to a global `~/.renyignore` if none is found) to cleanly exclude specific directories from processing. 

You can also explicitly pass any file, like a standard `.gitignore`, to automatically parse and exclude those paths from the output:
```bash
reny -r -el 2 -ig .gitignore
```
```text
~/Desktop/_Dev/reny
  |- LICENSE
  |- pyproject.toml
  |- README.md
  |- setup.py
  |->/reny
    |- __init__.py
    |->/cli
      |- __init__.py
      |-/base
      |-/renamer
    |->/commons
      |- __init__.py
      |- chainedhandler.py
      |- descriptors.py
      |- progressbar.py
      |- taskprocessor.py
      |- utils.py
    |->/fstools
      |- __init__.py
      |- dirtools.py
      |- fsutils.py
      |- rename.py
      |- virtual_organizer.py
      |- walker.py
      |-/builders
  |->/tests
    |- __init__.py
    |->/base
      |- __init__.py
      |- test_base.py
    |->/commons
      |- __init__.py
      |- test_commons.py
      |- test_ignore.py
    |->/fs
      |- __init__.py
      |- test_fs_base.py
      |- test_fs_organize.py
      |- test_fsutils.py
      |-/data
28 files, 12 folders
```

### Real-World Scenario: Downloads Cleanup
A safe, two-step workflow to tame a chaotic downloads folder by grouping files by their extension and sorting them by size to see what's eating up your disk space.

**Step 1: Preview the cleanup with size statistics**
*(Shows you the largest file categories first, without moving any files)*
```bash
reny -s sd print -b type -ss
```

**Step 2: Commit the organization**
*(Actually moves the files into their respective subdirectories)*
```bash
reny organize -b type
```

## Documentation & Tutorials
Although `reny` is a standalone project, its core organizing logic is inherited directly from [`batchmp`](https://github.com/akpw/batch-mp-tools). You can find detailed tutorials and deep-dives on how to master its capabilities in the original blog posts:
- [Renamer Organize & Virtual Views](https://akpw.github.io/articles/2025/09/22/Print-and-Organize.html) – *Highly recommended reading for mastering virtual directory views*
- [BatchMP Tools Tutorial, Part II: renaming files with renamer](https://akpw.github.io/articles/2015/04/11/batchmp-tutorial-part-ii.html)
- [Practical BatchMP Series](https://akpw.github.io//tags.html#BatchMP+Tools)

## Usage
Run `reny --help` to see all available filesystem operations!

## Development
To set up the project for development:

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
The project uses `pytest` for its test suite. Because `reny` performs real filesystem operations, the tests are designed to dynamically create and clean up safe temporary sandbox folders during execution.

To run the full test suite:
```bash
pytest -v --tb=short tests/
```

To run a specific test file:
```bash
pytest tests/fs/test_fs_organize.py
```
