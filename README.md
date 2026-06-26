# Reny
A lightweight, fast, and safe batch renaming and filesystem organization tool.

## Background
`reny` was originally born as the `renamer` component inside the larger [`batchmp`](https://github.com/akpw/batch-mp-tools) (Batch Media Processing) suite. It was spun off into its own standalone package to provide developers with an ultra-lightweight, pure-filesystem organizing tool without the heavy baggage of FFmpeg and Mutagen media dependencies. 

If you need advanced media operations (like denoising, cover-art extraction, or format transcoding), check out the original [`batchmp`](https://github.com/akpw/batch-mp-tools) project. If you just need to organize your files with surgical precision, `reny` is all you need!

## Installation
You can install `reny` globally using pipx:
```bash
pipx install .
```

## Features
- **Regex Replacement:** Powerful batch renaming using standard regular expressions.
- **Flattening:** Safely collapse nested directory structures into a single folder.
- **Virtual Views:** Preview how a directory will look when sorted by size, date, or type before making any changes.
- **Dry-Run by Default:** `reny` will always visualize targeted changes and ask for confirmation before it ever touches your files.

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
Although `reny` is a new standalone project, its core organizing logic is inherited directly from [`batchmp`](https://github.com/akpw/batch-mp-tools). You can find detailed tutorials and deep-dives on how to master its capabilities in the original blog posts:
- [Renamer Organize & Virtual Views](https://akpw.github.io/articles/2025/09/22/Print-and-Organize.html) – *Highly recommended reading for mastering virtual directory views!*
- [BatchMP Tools Tutorial, Part II: renaming files with renamer](https://akpw.github.io/articles/2015/04/11/batchmp-tutorial-part-ii.html)
- [Practical BatchMP Series](https://akpw.github.io//tags.html#BatchMP+Tools)

## Usage
Run `reny --help` to see all available filesystem operations!
