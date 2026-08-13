"""
Figure: Challenges reported by eleven consulted Ghanaian nonprofit
organisations, July 2026.

Reads the anonymised coding matrix from consultation_matrix.csv,
validates it, and generates the publication figure. To change the coding
after auditing against the call notes, edit the CSV, not this script.

Usage:  python3 consultation_matrix.py
Output: consultation_matrix.png (300 dpi) and consultation_matrix.pdf
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV_PATH = "consultation_matrix.csv"
EXPECTED_N = 11

THEME_LABELS = {
    "funding_volatility": "Funding\nvolatility",
    "core_support_deficit": "Core support\nabsent",
    "regulatory_burden": "Regulatory\nburden",
    "intl_funding_barriers": "Access\nbarriers",
    "volunteer_staffing": "Volunteer /\nstaffing",
    "capacity_structure_visibility": "Capacity /\nvisibility",
    "credit_model_risk": "Credit\nmodel",
}


def load_and_validate(path: str) -> pd.DataFrame:
    """Load the coding matrix and check its integrity before plotting."""
    df = pd.read_csv(path)
    theme_cols = list(THEME_LABELS)
    missing = [c for c in theme_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing expected theme columns: {missing}")
    if len(df) != EXPECTED_N:
        raise ValueError(f"Expected {EXPECTED_N} organisations, found {len(df)}")
    values = df[theme_cols].to_numpy()
    if not np.isin(values, (0, 1)).all():
        raise ValueError("Coding matrix must contain only 0 and 1")
    if df["organisation"].duplicated().any():
        raise ValueError("Duplicate organisation labels found")
    return df


def main() -> None:
    df = load_and_validate(CSV_PATH)
    orgs = df["organisation"].tolist()
    theme_cols = list(THEME_LABELS)
    matrix = df[theme_cols].to_numpy()
    THEMES = [THEME_LABELS[c] for c in theme_cols]

    # Order columns by how many organisations reported each theme,
    # most-reported first, so the figure reads as a ranking.
    order = np.argsort(-matrix.sum(axis=0), kind="stable")
    matrix = matrix[:, order]
    themes = [THEMES[j] for j in order]
    totals = matrix.sum(axis=0)

    labels = [f"{t.replace(chr(10), ' ')}  (n = {n})"
              for t, n in zip(themes, totals)]

    fig, ax = plt.subplots(figsize=(11.5, 6.4))

    ax.set_xlim(-0.5, len(themes) - 0.5)
    ax.set_ylim(len(orgs) - 0.5, -0.5)  # first organisation at the top

    for i in range(len(orgs)):
        for j in range(len(themes)):
            if matrix[i, j]:
                ax.scatter(j, i, s=170, marker="o",
                           color="#1a4d6e", zorder=3)

    for i in range(len(orgs)):
        ax.axhline(i, color="0.88", lw=0.7, zorder=1)
    for j in range(len(themes)):
        ax.axvline(j, color="0.93", lw=0.7, zorder=1)

    ax.set_xticks(range(len(themes)))
    ax.set_xticklabels(labels, fontsize=9.5, rotation=24,
                       ha="right", rotation_mode="anchor")
    ax.set_yticks(range(len(orgs)))
    ax.set_yticklabels(orgs, fontsize=9)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


    fig.tight_layout()
    fig.savefig("consultation_matrix.png", dpi=300, bbox_inches="tight")
    fig.savefig("consultation_matrix.pdf", bbox_inches="tight")
    print("Wrote consultation_matrix.png and consultation_matrix.pdf")
    print("Theme totals (ordered):",
          dict(zip([t.replace('\n', ' ') for t in themes],
                   totals.tolist())))


if __name__ == "__main__":
    main()
