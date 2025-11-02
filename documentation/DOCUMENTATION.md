# Detailed Documentation - movies_cleaning.py

## Purpose
This script standardizes and cleans movie CSV files. It performs text cleaning, numeric parsing, missing-value handling, basic feature engineering, outlier clipping, and optional scaling and plotting.

## Expected repository layout
- movies_cleaning.py
- uncleaned_files/  (input CSVs)
- cleaned_files/    (output CSVs)
- documentation/    (this file)

## Main steps performed by the script
1. Reads each `.csv` file from the `uncleaned_files` folder.
2. Drops duplicate rows.
3. Cleans text columns: `MOVIES`, `GENRE`, `ONE-LINE`, `STARS` (strip, remove newlines).
4. Extracts a 4-digit `YEAR` and converts to numeric where possible.
5. Parses `VOTES` by removing commas and converting to numeric.
6. Cleans `Gross` by removing non-numeric characters and converting to numeric.
7. Safely fills numeric columns (`RATING`, `VOTES`, `RunTime`, `Gross`) using column median when available.
8. Fills `GENRE` using the mode or `Unknown` when unavailable.
9. Adds `num_stars` and `num_genres` features.
10. Clips `RunTime` at the 99th percentile to reduce the effect of outliers.
11. Scales numeric columns (`RATING`, `VOTES`, `RunTime`, `Gross`) with `MinMaxScaler` when valid data exists.
12. Writes cleaned CSV to `cleaned_files` with a timestamped filename.
13. Optionally displays plots: missing values heatmap, rating histogram, runtime boxplot.

## Command-line options
- `--uncleaned_folder` : path to folder containing raw CSVs (default: `uncleaned_files`)
- `--cleaned_folder` : path to write cleaned CSVs (default: `cleaned_files`)
- `--no-plot` : disable plotting (useful for headless machines)
- `--verbose` : enable debug-level logging

## Implementation notes and rationale
- The script is defensive: it checks for required columns before operating and logs at INFO/DEBUG levels.
- Numeric fills use the median where possible. If a column has all missing values, median fill is skipped and the missing values remain.
- Mode fill for `GENRE` uses `'Unknown'` fallback to avoid empty strings in that column.
- Scaling uses `MinMaxScaler` only when a column has at least one non-NaN value to avoid failures.
- Plotting is wrapped in a try/except to prevent plotting errors from stopping the run.

## Known limitations
- The script assumes reasonably consistent column names across CSVs. If a CSV has different column names, the script will skip unavailable transformations.
- `Gross` values with suffixes like `M` (millions) are not interpreted (e.g., `1.2M` becomes `1.2`). Consider extending parsing if such formats appear.
- Scaling is done per-file; if you want a consistent scale across files, compute scaling parameters on a combined dataset.

## Suggested improvements
- Add unit tests for parsing routines (`YEAR`, `VOTES`, `Gross`).
- Add a `--merge` mode that concatenates cleaned files into a single merged CSV.
- Add flags to control which feature-engineering steps run (`--no-scale`, `--no-clip`).
- Replace `print` statements (if added) with structured `logging` (already done here).
- Add data validation (e.g., `great_expectations`) to assert invariants after cleaning.

## Example
```
python movies_cleaning.py --no-plot --verbose
```

This will process CSVs in `uncleaned_files` and write timestamped cleaned CSVs to `cleaned_files` while printing detailed logs.

## Contact
For questions or to contribute improvements, open an issue or create a pull request in this repository.

## CI/CD Pipeline Setup

This project uses GitHub Actions for Continuous Integration (CI). The pipeline ensures that the script runs successfully on sample data whenever changes are pushed to the `main` branch or a pull request is created.

### Steps to Set Up CI/CD

1. **Create a GitHub repository**:
   - Initialize a Git repository locally (if not already done):
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     ```
   - Push the repository to GitHub:
     ```bash
     git remote add origin <repository-url>
     git branch -M main
     git push -u origin main
     ```

2. **Add GitHub Actions workflow**:
   - Create a `.github/workflows/ci.yml` file in the repository root with the following content:
     ```yaml
     name: CI Pipeline

     on:
       push:
         branches:
           - main
       pull_request:
         branches:
           - main

     jobs:
       test:
         runs-on: ubuntu-latest

         steps:
         - name: Checkout code
           uses: actions/checkout@v3

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.8'

         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt

         - name: Run script on sample data
           run: |
             mkdir -p uncleaned_files cleaned_files
             echo "MOVIES,YEAR,GENRE,RATING,ONE-LINE,STARS,VOTES,RunTime,Gross" > uncleaned_files/sample.csv
             echo "Sample Movie,2021,Action,8.5,An action-packed movie,Star1,1000,120,500000" >> uncleaned_files/sample.csv
             python movies_cleaning.py --no-plot --verbose

         - name: Verify output
           run: |
             if [ ! -f cleaned_files/sample_cleaned_*.csv ]; then
               echo "Cleaned file not found!" && exit 1
             fi

         - name: Linting (optional)
           run: |
             echo "Linting step can be added here if needed."
     ```

3. **Commit and push the workflow**:
   - Add the workflow file to Git:
     ```bash
     git add .github/workflows/ci.yml
     git commit -m "Add CI pipeline"
     git push
     ```

4. **Verify the pipeline**:
   - Open the GitHub repository in your browser.
   - Navigate to the "Actions" tab.
   - Ensure the workflow runs successfully on the `main` branch or pull requests.

### Extending the Pipeline
- **Add linting**: Use tools like `flake8` or `pylint` to enforce code quality.
- **Add unit tests**: Include a `tests/` folder with test cases and run them in the pipeline.
- **Add deployment**: Extend the pipeline to deploy cleaned files or artifacts to a cloud storage bucket or server.

### Troubleshooting
- If the pipeline fails, check the logs in the "Actions" tab on GitHub.
- Ensure `requirements.txt` is up-to-date with all dependencies.
- Verify that the script runs locally before pushing changes.

For further assistance, refer to the [GitHub Actions documentation](https://docs.github.com/en/actions).
