#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import logging
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

plt.rcParams['figure.figsize'] = (8, 5)


# Replaced ad-hoc script with a safer, CLI-driven implementation.


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s: %(message)s")


def safe_median_fill(series: pd.Series, logger: logging.Logger):
    """Fill NaNs in numeric series with median when possible.
    If median is NaN (e.g., all values missing), leave as-is and log.
    """
    try:
        median = series.median()
        if pd.isna(median):
            logger.debug("Median is NaN for column '%s' - skipping median fill", series.name)
            return series
        return series.fillna(median)
    except Exception:
        logger.exception("Failed to compute/fill median for %s", series.name)
        return series


def clean_dataframe(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    df = df.copy()

    logger.debug("Starting shape: %s", df.shape)
    # Drop duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count:
        logger.info("Dropping %d duplicate rows", int(dup_count))
        df = df.drop_duplicates()

    # Clean text columns
    text_cols = ['MOVIES', 'GENRE', 'ONE-LINE', 'STARS']
    for col in text_cols:
        if col in df.columns:
            # Convert to string, remove newlines, trim
            df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()

    # Extract 4-digit year
    if 'YEAR' in df.columns:
        df['YEAR'] = df['YEAR'].astype(str).str.extract(r'(\d{4})')
        df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')

    # Convert VOTES (remove commas)
    if 'VOTES' in df.columns:
        df['VOTES'] = df['VOTES'].astype(str).str.replace(',', '', regex=True)
        df['VOTES'] = pd.to_numeric(df['VOTES'], errors='coerce')

    # Clean Gross (remove non-numeric characters)
    if 'Gross' in df.columns:
        df['Gross'] = df['Gross'].astype(str).str.replace('[^0-9.]', '', regex=True)
        df['Gross'] = pd.to_numeric(df['Gross'], errors='coerce')
        # Do not blindly fill all NaNs with 0; leave NaN to be handled by median fill below if appropriate

    # Handle missing values for numeric columns safely
    numeric_cols = ['RATING', 'VOTES', 'RunTime', 'Gross']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = safe_median_fill(df[col], logger)

    # Fill GENRE with mode if possible
    if 'GENRE' in df.columns:
        try:
            mode_vals = df['GENRE'].mode()
            if len(mode_vals) > 0 and pd.notna(mode_vals.iloc[0]):
                df['GENRE'] = df['GENRE'].fillna(mode_vals.iloc[0])
            else:
                df['GENRE'] = df['GENRE'].fillna('Unknown')
        except Exception:
            logger.exception("Failed to compute mode for GENRE; filling missing with 'Unknown'")
            df['GENRE'] = df['GENRE'].fillna('Unknown')

    # Feature engineering
    if 'STARS' in df.columns:
        df['num_stars'] = df['STARS'].apply(lambda x: len([s for s in str(x).split(',') if s.strip()]))

    if 'GENRE' in df.columns:
        df['num_genres'] = df['GENRE'].apply(lambda x: len([g for g in str(x).split(',') if g.strip()]))

    # Clip RunTime extremes at 99th percentile
    if 'RunTime' in df.columns and df['RunTime'].dropna().size > 0:
        try:
            upper = df['RunTime'].quantile(0.99)
            df.loc[df['RunTime'] > upper, 'RunTime'] = upper
        except Exception:
            logger.exception("Failed to compute/clip RunTime quantile")

    # Scale numeric columns using MinMaxScaler when there is valid data
    scaler_cols = [c for c in ['RATING', 'VOTES', 'RunTime', 'Gross'] if c in df.columns]
    if scaler_cols:
        try:
            # Only scale columns that have at least one non-NaN value
            valid_cols = [c for c in scaler_cols if df[c].dropna().size > 0]
            if valid_cols:
                scaler = MinMaxScaler()
                df[valid_cols] = scaler.fit_transform(df[valid_cols].astype(float))
            else:
                logger.debug("No valid numeric columns found for scaling: %s", scaler_cols)
        except Exception:
            logger.exception("Failed during MinMax scaling")

    logger.debug("Finished shape: %s", df.shape)
    return df


def safe_plot(df: pd.DataFrame, filename: str, no_plot: bool, logger: logging.Logger):
    if no_plot:
        logger.debug("Skipping plotting (no_plot=True)")
        return

    try:
        sns.heatmap(df.isna(), cbar=False)
        plt.title(f"Missing Values After Cleaning: {filename}")
        plt.show()

        if 'RATING' in df.columns:
            sns.histplot(df['RATING'].dropna(), bins=20)
            plt.title(f"Rating Distribution (scaled): {filename}")
            plt.show()

        if 'RunTime' in df.columns:
            sns.boxplot(x=df['RunTime'].dropna())
            plt.title(f"RunTime (after clipping): {filename}")
            plt.show()
    except Exception:
        logger.exception("Plotting failed - continuing without plots")


def process_file(input_path: str, cleaned_folder: str, no_plot: bool, logger: logging.Logger) -> str:
    logger.info("Processing file: %s", input_path)
    try:
        df = pd.read_csv(input_path)
    except Exception:
        logger.exception("Failed to read CSV: %s", input_path)
        return ""

    logger.info("Initial shape: %s", df.shape)

    df_clean = clean_dataframe(df, logger)

    # Prepare output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f"{base}_cleaned_{timestamp}.csv"
    output_path = os.path.join(cleaned_folder, output_filename)

    try:
        df_clean.to_csv(output_path, index=False)
        logger.info("Saved cleaned file to: %s", output_path)
    except Exception:
        logger.exception("Failed to save cleaned CSV to %s", output_path)

    # Optional plotting
    safe_plot(df_clean, os.path.basename(input_path), no_plot, logger)

    logger.debug("First 5 rows:\n%s", df_clean.head(5).to_string())
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Clean movie CSV files in a folder and write cleaned versions to an output folder.")
    parser.add_argument('--uncleaned_folder', default='uncleaned_files', help='Input folder with raw CSV files')
    parser.add_argument('--cleaned_folder', default='cleaned_files', help='Output folder for cleaned CSV files')
    parser.add_argument('--no-plot', action='store_true', help='Disable plotting (useful for headless runs)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args(argv)

    setup_logging(args.verbose)
    logger = logging.getLogger()

    # Ensure folders exist
    os.makedirs(args.uncleaned_folder, exist_ok=True)
    os.makedirs(args.cleaned_folder, exist_ok=True)

    found = False
    for filename in sorted(os.listdir(args.uncleaned_folder)):
        if filename.lower().endswith('.csv'):
            found = True
            input_path = os.path.join(args.uncleaned_folder, filename)
            process_file(input_path, args.cleaned_folder, args.no_plot, logger)

    if not found:
        logger.warning("No CSV files found in %s", args.uncleaned_folder)


if __name__ == '__main__':
    main()
