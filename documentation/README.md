# Movies Cleaning Project - Quick Start

This repository contains a small data-cleaning utility `movies_cleaning.py` that processes CSV files placed in `uncleaned_files/` and writes cleaned versions to `cleaned_files/`.

Requirements
- Python 3.8+
- Packages listed in `requirements.txt` (recommended to install in a virtual environment)

Install dependencies
```
python -m pip install -r requirements.txt
```

Quick run (headless, no plots)
```
python movies_cleaning.py --no-plot
```

Default folders
- `uncleaned_files/` : place raw CSVs here
- `cleaned_files/` : cleaned CSVs will be written here

Options
- `--uncleaned_folder`: path to input folder (default `uncleaned_files`)
- `--cleaned_folder`: path to output folder (default `cleaned_files`)
- `--no-plot`: disable plotting (recommended for servers)
- `--verbose`: enable verbose logging

If you need a persistent filename instead of timestamped outputs, run the script and rename/move the output file as preferred.

For full details, see `documentation/DOCUMENTATION.md`.

