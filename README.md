# Reny
A lightweight, fast, and safe batch renaming and filesystem organization tool.

## Background
`reny` was originally created as the `renamer` component inside the larger [`batchmp`](https://github.com/akpw/batch-mp-tools) (Batch Media Processing) suite. It was spun off into its own standalone package to provide for an ultra-lightweight, safe, pure-filesystem organizing tool without FFmpeg / Mutagen media dependencies. 

If you need advanced media operations (like denoising, cover-art extraction, or format transcoding), check out the original [`batchmp`](https://github.com/akpw/batch-mp-tools) project. If you just need to safely organize your files with surgical precision, `reny` is all you need.

## Installation
You can install `reny` globally using pipx:
```bash
pipx install .
```

## Features
- **Virtual Views:** Preview how a directory structure would look when reorganised by type, size, or date without moving or changing anything
- **Indexing:** Multi-level indexing across nested directories, supporting multiple indexing schemes
- **Padding:** Automatically pad existing numbers in filenames with leading zeros to fix sorting orders
- **Flattening:** Safely collapse nested directory structures into a single folder
- **Regex Replacement:** Powerful batch renaming using standard regular expressions
- **Dry-Run by Default:** `reny` will always visualize targeted changes and ask for confirmation before it ever touches your files

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

## Documentation & Tutorials
Although `reny` is a standalone project, its core organizing logic is inherited directly from [`batchmp`](https://github.com/akpw/batch-mp-tools). You can find detailed tutorials and deep-dives on how to master its capabilities in the original blog posts:
- [Renamer Organize & Virtual Views](https://akpw.github.io/articles/2025/09/22/Print-and-Organize.html) – *Highly recommended reading for mastering virtual directory views*
- [BatchMP Tools Tutorial, Part II: renaming files with renamer](https://akpw.github.io/articles/2015/04/11/batchmp-tutorial-part-ii.html)
- [Practical BatchMP Series](https://akpw.github.io//tags.html#BatchMP+Tools)

## Usage
Run `reny --help` to see all available filesystem operations
