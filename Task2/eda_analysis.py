"""
Exploratory Data Analysis (EDA) Script
========================================
Project 2: Exploratory Data Analysis

Goal:
    Analyze a dataset to understand patterns, trends, and distributions.

What this script does:
    1. Loads the dataset (Excel/CSV)
    2. Calculates basic descriptive statistics (mean, median, count, std, min, max)
       for numeric columns and frequency counts for categorical columns
    3. Identifies outliers using the IQR (Interquartile Range) method
    4. Identifies trends over time (monthly/yearly)
    5. Generates visualizations (histograms, boxplots, trend line, bar charts,
       correlation heatmap)
    6. Summarizes key observations in a plain-text report

Usage:
    python eda_analysis.py --file "Dataset_for_Data_Analytics.xlsx" --outdir "eda_output"

    If --file is not provided, the script looks for
    "Dataset_for_Data_Analytics.xlsx" in the current directory.

Requirements:
    pandas, numpy, matplotlib, seaborn, openpyxl
    (install with: pip install pandas numpy matplotlib seaborn openpyxl)
"""

import argparse
import os
import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for scripts/servers
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def load_data(filepath: str) -> pd.DataFrame:
    """Load a dataset from .xlsx, .xls, or .csv into a DataFrame."""
    if not os.path.exists(filepath):
        sys.exit(f"ERROR: File not found -> {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    elif ext == ".csv":
        df = pd.read_csv(filepath)
    else:
        sys.exit(f"ERROR: Unsupported file type '{ext}'. Use .xlsx, .xls, or .csv")

    print(f"Loaded '{filepath}' -> {df.shape[0]} rows x {df.shape[1]} columns\n")
    return df


def detect_date_column(df: pd.DataFrame):
    """Return the name of the first column that looks like a date column."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
        if "date" in col.lower():
            try:
                pd.to_datetime(df[col])
                return col
            except Exception:
                continue
    return None


def get_column_types(df: pd.DataFrame):
    """Split columns into numeric and categorical groups."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    return numeric_cols, categorical_cols


def iqr_outliers(series: pd.Series):
    """Identify outliers in a numeric series using the IQR method.
    Returns (outlier_values, lower_bound, upper_bound)."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = series[(series < lower) | (series > upper)]
    return outliers, lower, upper


# --------------------------------------------------------------------------- #
# Analysis steps
# --------------------------------------------------------------------------- #

def basic_statistics(df: pd.DataFrame, numeric_cols: list, report: list):
    report.append("=" * 70)
    report.append("1. BASIC STATISTICS (numeric columns)")
    report.append("=" * 70)

    stats = df[numeric_cols].agg(["count", "mean", "median", "std", "min", "max"]).T
    stats = stats.round(2)
    report.append(stats.to_string())
    report.append("")

    print(stats)
    return stats


def categorical_summary(df: pd.DataFrame, categorical_cols: list, report: list, top_n: int = 5):
    report.append("=" * 70)
    report.append("2. CATEGORICAL COLUMN SUMMARY (top categories)")
    report.append("=" * 70)

    for col in categorical_cols:
        n_unique = df[col].nunique()
        report.append(f"\n[{col}]  -> {n_unique} unique values")
        if n_unique <= 50:  # skip near-unique ID-like columns
            counts = df[col].value_counts(dropna=False).head(top_n)
            report.append(counts.to_string())
    report.append("")


def missing_values(df: pd.DataFrame, report: list):
    report.append("=" * 70)
    report.append("3. MISSING VALUES")
    report.append("=" * 70)

    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
    missing_df = missing_df[missing_df["missing_count"] > 0].sort_values(
        "missing_count", ascending=False
    )

    if missing_df.empty:
        report.append("No missing values detected in any column.")
    else:
        report.append(missing_df.to_string())
    report.append("")


def outlier_analysis(df: pd.DataFrame, numeric_cols: list, report: list):
    report.append("=" * 70)
    report.append("4. OUTLIER DETECTION (IQR method)")
    report.append("=" * 70)

    outlier_summary = {}
    for col in numeric_cols:
        outliers, lower, upper = iqr_outliers(df[col].dropna())
        outlier_summary[col] = len(outliers)
        report.append(
            f"[{col}] normal range: [{lower:.2f}, {upper:.2f}]  "
            f"-> {len(outliers)} outlier(s) ({len(outliers) / len(df) * 100:.1f}%)"
        )
    report.append("")
    return outlier_summary


def trend_analysis(df: pd.DataFrame, date_col: str, value_col: str, report: list, outdir: str):
    report.append("=" * 70)
    report.append(f"5. TREND ANALYSIS OVER TIME ('{value_col}' by month)")
    report.append("=" * 70)

    tmp = df[[date_col, value_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp["year_month"] = tmp[date_col].dt.to_period("M")

    monthly = tmp.groupby("year_month")[value_col].agg(["sum", "mean", "count"]).round(2)
    report.append(monthly.to_string())
    report.append("")

    # Trend direction (first half vs second half average)
    half = len(monthly) // 2
    if half > 0:
        first_half_avg = monthly["sum"].iloc[:half].mean()
        second_half_avg = monthly["sum"].iloc[half:].mean()
        direction = "increasing" if second_half_avg > first_half_avg else "decreasing"
        pct_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        report.append(
            f"Overall trend: {direction} "
            f"({pct_change:+.1f}% change, first-half avg {first_half_avg:.2f} "
            f"-> second-half avg {second_half_avg:.2f} per month)"
        )
    report.append("")

    # Plot
    plt.figure(figsize=(11, 5))
    monthly["sum"].plot(marker="o")
    plt.title(f"Monthly Trend: Total {value_col}")
    plt.xlabel("Month")
    plt.ylabel(f"Total {value_col}")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "trend_monthly.png"), dpi=150)
    plt.close()

    return monthly


def correlation_analysis(df: pd.DataFrame, numeric_cols: list, report: list, outdir: str):
    report.append("=" * 70)
    report.append("6. CORRELATION BETWEEN NUMERIC VARIABLES")
    report.append("=" * 70)

    if len(numeric_cols) < 2:
        report.append("Not enough numeric columns for correlation analysis.")
        report.append("")
        return None

    corr = df[numeric_cols].corr().round(2)
    report.append(corr.to_string())
    report.append("")

    plt.figure(figsize=(7, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "correlation_heatmap.png"), dpi=150)
    plt.close()

    return corr


def generate_visuals(df: pd.DataFrame, numeric_cols: list, categorical_cols: list, outdir: str):
    # Histograms for numeric columns
    n = len(numeric_cols)
    if n > 0:
        fig, axes = plt.subplots(nrows=(n + 2) // 3, ncols=3, figsize=(15, 4 * ((n + 2) // 3)))
        axes = np.array(axes).flatten()
        for i, col in enumerate(numeric_cols):
            sns.histplot(df[col].dropna(), kde=True, ax=axes[i], color="steelblue")
            axes[i].set_title(f"Distribution of {col}")
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "histograms.png"), dpi=150)
        plt.close()

        # Boxplots to visualize outliers
        fig, axes = plt.subplots(nrows=(n + 2) // 3, ncols=3, figsize=(15, 4 * ((n + 2) // 3)))
        axes = np.array(axes).flatten()
        for i, col in enumerate(numeric_cols):
            sns.boxplot(x=df[col].dropna(), ax=axes[i], color="salmon")
            axes[i].set_title(f"Boxplot of {col}")
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "boxplots.png"), dpi=150)
        plt.close()

    # Bar charts for top categorical columns (skip near-unique ID columns)
    plot_cats = [c for c in categorical_cols if df[c].nunique() <= 15]
    if plot_cats:
        fig, axes = plt.subplots(nrows=(len(plot_cats) + 1) // 2, ncols=2,
                                  figsize=(13, 4 * ((len(plot_cats) + 1) // 2)))
        axes = np.array(axes).flatten()
        for i, col in enumerate(plot_cats):
            counts = df[col].value_counts(dropna=False).head(10)
            sns.barplot(x=counts.values, y=counts.index.astype(str), ax=axes[i], color="teal")
            axes[i].set_title(f"Top categories in {col}")
            axes[i].set_xlabel("Count")
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "categorical_bar_charts.png"), dpi=150)
        plt.close()


def key_observations(df: pd.DataFrame, numeric_cols: list, categorical_cols: list,
                      outlier_summary: dict, report: list):
    report.append("=" * 70)
    report.append("7. KEY OBSERVATIONS (auto-generated summary)")
    report.append("=" * 70)

    obs = []
    obs.append(f"- Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")

    # Numeric highlights
    for col in numeric_cols:
        mean_v = df[col].mean()
        median_v = df[col].median()
        skew_note = "right-skewed" if mean_v > median_v * 1.1 else (
            "left-skewed" if mean_v < median_v * 0.9 else "roughly symmetric"
        )
        obs.append(
            f"- '{col}': mean={mean_v:.2f}, median={median_v:.2f} -> distribution looks {skew_note}."
        )

    # Outliers
    for col, count in outlier_summary.items():
        if count > 0:
            pct = count / len(df) * 100
            obs.append(f"- '{col}' has {count} outlier(s) ({pct:.1f}% of records).")

    # Categorical highlights
    for col in categorical_cols:
        if df[col].nunique() <= 50:
            top_val = df[col].value_counts(dropna=False).idxmax()
            top_pct = df[col].value_counts(dropna=False, normalize=True).max() * 100
            obs.append(f"- Most common value in '{col}' is '{top_val}' ({top_pct:.1f}% of records).")

    report.extend(obs)
    report.append("")
    return obs


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Exploratory Data Analysis (EDA) script")
    parser.add_argument("--file", type=str, default="Dataset_for_Data_Analytics.xlsx",
                         help="Path to the dataset file (.xlsx, .xls, or .csv)")
    parser.add_argument("--outdir", type=str, default="eda_output",
                         help="Directory where charts and the report will be saved")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    report = []
    report.append("EXPLORATORY DATA ANALYSIS REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Source file: {args.file}")
    report.append("")

    df = load_data(args.file)
    numeric_cols, categorical_cols = get_column_types(df)
    date_col = detect_date_column(df)

    print("Numeric columns:", numeric_cols)
    print("Categorical columns:", categorical_cols)
    print("Detected date column:", date_col)
    print()

    # 1. Basic statistics
    basic_statistics(df, numeric_cols, report)

    # 2. Categorical summary
    categorical_summary(df, categorical_cols, report)

    # 3. Missing values
    missing_values(df, report)

    # 4. Outlier detection
    outlier_summary = outlier_analysis(df, numeric_cols, report)

    # 5. Trend analysis (only if a date column and a meaningful numeric value column exist)
    if date_col and numeric_cols:
        # Prefer a column that looks like a monetary/total value; else use the first numeric col
        priority_keywords = ["total", "revenue", "amount", "sales", "price"]
        value_col = None
        for kw in priority_keywords:
            match = next((c for c in numeric_cols if kw in c.lower()), None)
            if match:
                value_col = match
                break
        if value_col is None:
            value_col = numeric_cols[0]
        trend_analysis(df, date_col, value_col, report, args.outdir)
    else:
        report.append("=" * 70)
        report.append("5. TREND ANALYSIS OVER TIME")
        report.append("=" * 70)
        report.append("Skipped: no date column and/or numeric column detected.")
        report.append("")

    # 6. Correlation
    correlation_analysis(df, numeric_cols, report, args.outdir)

    # Visualizations
    generate_visuals(df, numeric_cols, categorical_cols, args.outdir)

    # 7. Key observations
    key_observations(df, numeric_cols, categorical_cols, outlier_summary, report)

    # Save report
    report_path = os.path.join(args.outdir, "eda_report.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(report))

    print("\n" + "=" * 70)
    print(f"Analysis complete. Report and charts saved to: {args.outdir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
