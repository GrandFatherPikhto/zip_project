# zip_project 📦

A universal Python console utility for automatic archiving and generating file listings of your engineering and software projects. Perfect for quickly creating source code backups, preparing releases, or cleaning projects from temporary clutter (like `__pycache__`, `.venv`, `.git`) before sharing.

---

## 🚀 Key Features

*   **Smart config search**: Automatically looks for `zip_project.yaml` in the executable's folder, then in the current working directory. Creates a template if missing.
*   **Flexible filtering**: Exclude junk using **glob patterns** (with `**` for recursive matching), by extensions, by file size, and by modification date.
*   **Two output modes**: Generate a plain text manifest (plain, JSON, CSV) with optional metadata (size, date), pack into an archive (zip or tar.gz) – or both.
*   **CLI overrides**: All config keys can be overridden via command-line arguments without editing YAML – ideal for CI/CD.
*   **Environment variables**: Use `${HOME}` or `$PROJECT_DIR` in config values for portability.
*   **Dry run** (`--dry-run`): Shows which files would be processed without writing anything to disk.
*   **Fully portable**: Compiled into a single `.exe` with PyInstaller, runs without Python installation.

---

## ⚙️ Detailed Configuration (`zip_project.yaml`)

The configuration file uses YAML format and is automatically created on the first run in the folder where the config is missing.  
Below is the **new extended structure** with all available parameters:

```yaml
# ==============================================================================
# GENERAL SETTINGS
# ==============================================================================

# Project name (optional, for information)
project_name: "MyProject"

# Base working directory (absolute or relative path).
# Can be a string or a list of paths – then scanning will start from multiple roots.
# Paths are interpreted relative to the folder containing the config file.
base_working_dir: "."

# Encoding for reading/writing files (default utf-8)
encoding: "utf-8"

# Dry run: true – only show file list, do not write anything
dry_run: false

# ==============================================================================
# WHAT TO SCAN
# ==============================================================================

# Folders to traverse recursively (relative to base_working_dir)
scan_dirs:
  - "src"
  - "modules"

# Specific files to include (in addition to scanning folders)
single_files:
  - "main.py"
  - "config.py"

# File extensions to include in the result (empty means all files)
extensions:
  - ".py"
  - ".yaml"

# ==============================================================================
# EXCLUSIONS (GLOB PATTERNS)
# ==============================================================================

# Patterns to exclude – supports ** (any nesting), * and ?
exclude_patterns:
  - "**/__pycache__"
  - "**/*.pyc"
  - "**/.venv"
  - "**/venv"
  - "**/.git"
  - "**/temp/*"
  - "**/local_settings.py"
  - "**/.env"

# Additionally – exclude files with certain extensions
exclude_extensions:
  - ".log"
  - ".tmp"

# ==============================================================================
# SIZE AND DATE RESTRICTIONS
# ==============================================================================

# Maximum file size in MB (null – no limit)
max_file_size_mb: 10

# Minimum file age in days (0 – only today's files, null – all)
min_file_age_days: null

# ==============================================================================
# OUTPUT MANIFEST (FILE LIST)
# ==============================================================================

manifest:
  # Name of the list file
  file: "project_list.txt"

  # Format: plain (simple list), json, csv
  format: "plain"

  # Whether to include metadata (size and modification time) in the manifest
  include_metadata: false

# ==============================================================================
# ARCHIVING
# ==============================================================================

archive:
  # Enable archive creation
  enabled: true

  # Archive file name (can include subfolders)
  file: "arch/project_backup.zip"

  # Format: zip or tar.gz
  format: "zip"

  # Compression level (0 – no compression, 9 – maximum)
  compression_level: 6

  # Password for ZIP archive (experimental, may not be supported)
  password: null
```

---

## 🛠️ New Features in Detail

### 🌐 Glob Patterns
Now you can exclude entire branches of the file system with a single pattern:
- `"**/__pycache__"` – excludes all `__pycache__` folders at any depth.
- `"tests/**/temp/*"` – excludes all temporary files inside `temp` folders located in any subdirectory of `tests`.
- `"*.tmp"` – excludes files with `.tmp` extension in the root (but not in subfolders unless you add `**`).

### 📦 Multiple Base Directories
If you specify `base_working_dir` as a list, for example:
```yaml
base_working_dir:
  - "backend"
  - "frontend"
```
scanning will be performed from each specified folder, and relative paths in the manifest and archive will be built relative to the corresponding base.

### 📄 Manifest Formats
- **plain** – each line contains a relative path to the file.
- **json** – structured list of objects (if metadata enabled, each object contains `path`, `size`, `mtime`).
- **csv** – table with columns `path`, `size`, `mtime` (if metadata enabled).

### ⏱️ Date and Size Filtering
- `max_file_size_mb: 5` – excludes files larger than 5 MB.
- `min_file_age_days: 30` – includes only files modified within the last 30 days (0 – only today).

### 🔒 Environment Variables
You can use `${VAR}` or `$VAR` in any string value in the config – they will be replaced with values from `os.environ`. This is convenient for specifying paths to projects in different environments.

---

## 💻 Running and Usage

### Config Search Order
1. **Explicitly specified argument** – `zip_project.exe /path/to/config.yaml`.
2. **Next to the executable** (or script) – `./zip_project.yaml`.
3. **In the current working directory** – `./zip_project.yaml`.
4. If nothing is found – a template is created in the current working directory.

### Basic Launch
```bash
zip_project                          # uses found or created config
zip_project my_config.yaml           # explicitly specify config
```

### Command Line Arguments (CLI Overrides)
All parameters below **take precedence** over values from YAML:

| Argument | Description | Example |
|----------|-------------|---------|
| `--base-dir DIR` | Overrides `base_working_dir` | `--base-dir ./src` |
| `--include-dir DIR` | Adds a folder to scan (can be repeated) | `--include-dir lib --include-dir tests` |
| `--exclude PATTERN` | Adds an exclusion pattern (can be repeated) | `--exclude "**/old" --exclude "*.tmp"` |
| `--output FILE` | Overrides the manifest file name | `--output files.txt` |
| `--zip` | Enables archive creation (even if `enabled: false` in config) | `--zip` |
| `--dry-run` | Only show file list, do not write anything | `--dry-run` |

**Examples:**
```bash
# Use config but change base folder and add an exclusion
zip_project --base-dir ./project --exclude "**/backup"

# Enable archiving and dry run
zip_project --zip --dry-run

# Override output file and add a scan folder
zip_project my_config.yaml --output list.txt --include-dir extra
```

### Precedence of Settings
**CLI arguments > environment variables > values from YAML > defaults**

---

## 🧪 Example Run

**Project structure:**
```
📁 my_project/
├── 📁 src/
│   ├── main.py
│   └── utils.py
├── 📁 __pycache__/       (will be excluded)
├── 📁 .venv/             (will be excluded)
├── .env                  (will be excluded)
└── zip_project.yaml
```

**Config:**
```yaml
base_working_dir: "."
scan_dirs: ["."]
extensions: [".py"]
exclude_patterns: ["**/__pycache__", "**/.venv", "**/.env"]
archive:
  enabled: true
  file: "backup.zip"
```

**Result:**
- `backup.zip` will be created, containing `src/main.py` and `src/utils.py`.
- Also `project_list.txt` (default name) will be created with the list of these files.

---

## 📦 Compiling to EXE (for Developers)

### Installing Dependencies
Before compiling, install the required packages:
```bash
pip install pyyaml pydantic
```

### Building with PyInstaller
```bash
pyinstaller --onefile --hidden-import yaml --hidden-import pydantic --name zip_project zip_project.py
```
It is recommended to specify `--distpath` to save to your utilities folder, for example:
```bash
pyinstaller --onefile --distpath D:\Utils --hidden-import yaml --hidden-import pydantic --name zip_project zip_project.py
```

### Quick Rebuild via `.spec`
On the first compilation, PyInstaller creates a `zip_project.spec` file. For subsequent code changes, simply run:
```bash
pyinstaller zip_project.spec
```
All settings (paths, hidden imports, flags) will be picked up automatically.

---

## ❓ Frequently Asked Questions

**How to exclude system files like `.DS_Store`?**  
Add `"**/.DS_Store"` to `exclude_patterns`.

**Can I use the config without archiving, only a list?**  
Yes, set `archive.enabled: false` or omit `--zip`.

**What if I need to process files from multiple unrelated folders?**  
Use `base_working_dir` as a list, or specify several `--include-dir`.

**How to see which files will be processed before the actual run?**  
Enable `dry_run: true` in the config or pass `--dry-run` in CLI.

---

## 📄 License

MIT — use, modify, distribute as you wish.  
Author: GrandFatherPikhto