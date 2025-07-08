import os
import pandas as pd
import matplotlib.pyplot as plt
from config.configuration import Config

# Load the data
file_path = os.path.join(Config.DataPaths.PROCESSED_DATA_DIR, "clothing_measurement_data.csv")
df = pd.read_csv(file_path)

def average_symmetric_parts(df, value_col="Icl"):
    """
    Average left and right body parts (e.g., "Left Hand" and "Right Hand" -> "Hand").
    Keeps other asymmetric or whole-body parts (like "All") unchanged.
    If only one side (Left or Right) is available for a condition, that value is used as-is.
    """
    parts = df["BodyPart"].unique()
    symmetric_pairs = []

    # Find matching left/right pairs
    for part in parts:
        if part.startswith("Left "):
            counterpart = part.replace("Left ", "Right ")
            symmetric_pairs.append((part, counterpart))

    new_rows = []
    processed = set()

    # Average or use available values from left/right pairs
    for left, right in symmetric_pairs:
        for condition in df["ClothingCondition"].unique():
            left_val = df[(df.BodyPart == left) & (df.ClothingCondition == condition)]["Icl"].values
            right_val = df[(df.BodyPart == right) & (df.ClothingCondition == condition)]["Icl"].values

            if left_val.size > 0 and right_val.size > 0:
                mean_val = (left_val[0] + right_val[0]) / 2
            elif left_val.size > 0:
                mean_val = left_val[0]
            elif right_val.size > 0:
                mean_val = right_val[0]
            else:
                continue  # No data for this condition

            new_rows.append({
                "BodyPart": left.replace("Left ", ""),
                "ClothingCondition": condition,
                "Icl": mean_val
            })

        processed.add(left)
        processed.add(right)

    # Keep unmatched parts as-is
    remaining = df[~df["BodyPart"].isin(processed)].copy()
    for row in new_rows:
        remaining = pd.concat([remaining, pd.DataFrame([row])], ignore_index=True)

    return remaining


def plot_icls_bar(df, annotate=True):
    """
    Bar plot of Icl values by body part.
    Adds optional annotation on top of each bar.
    """
    Config.PlotConfig.apply()

    ordered_parts = df["BodyPart"].drop_duplicates().tolist()
    df["ClothingCondition"] = df["ClothingCondition"].replace({"Summer": "Summer Clothing", "Winter": "Winter Clothing"})
    df_pivot = df.pivot(index="BodyPart", columns="ClothingCondition", values="Icl")
    df_pivot = df_pivot.reindex(ordered_parts)

    ax = df_pivot.plot(kind="bar")

    if annotate:
        for i, (idx, row) in enumerate(df_pivot.iterrows()):
            for j, (cond, val) in enumerate(row.items()):
                if pd.notna(val):
                    ax.text(i + (j - 0.5) * 0.4, val + 0.02, f"{val:.2f}", ha='center', va='bottom', fontsize=Config.PlotConfig.FONT_SIZE_SMALL)

    ax.set_ylabel("Intrinsic Clothing Insulation, $\it{I}_{cl}$ (clo)")
    ax.set_xlabel("")  # Remove x-axis label
    ax.set_title("Local Clothing Insulation", fontsize=Config.PlotConfig.FONT_SIZE_LARGE)
    ax.legend(title="")
    plt.xticks(rotation=45, ha="right")
    plt.yticks()
    plt.figtext(0.5, -0.05, "※ Body parts with both left and right sides were averaged.", ha="center")
    plt.tight_layout()
    plt.savefig(os.path.join(Config.FigurePaths.CLOTHING_DIR, "clothing_measurement_data.svg"), format="svg")
    plt.show()


# Main execution
df_avg = average_symmetric_parts(df, value_col="Icl")
plot_icls_bar(df_avg, annotate=True)
