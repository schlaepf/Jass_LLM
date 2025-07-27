import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ensure plots directory exists
os.makedirs("plots", exist_ok=True)


df = pd.read_csv("game_stats.csv", header=None, names=[
    "game_id", "round", "name_player1", "points_player1", 
    "name_player2", "points_player2", "name_player3", "points_player3", 
    "name_player4", "points_player4"
])

melted = pd.concat(
    [
        df[["game_id", "round", "name_player1", "points_player1"]].rename(
            columns={"name_player1": "player", "points_player1": "points"}
        ),
        df[["game_id", "round", "name_player2", "points_player2"]].rename(
            columns={"name_player2": "player", "points_player2": "points"}
        ),
        df[["game_id", "round", "name_player3", "points_player3"]].rename(
            columns={"name_player3": "player", "points_player3": "points"}
        ),
        df[["game_id", "round", "name_player4", "points_player4"]].rename(
            columns={"name_player4": "player", "points_player4": "points"}
        ),
    ],
    ignore_index=True,
)

wins = melted.loc[melted.groupby("game_id")["points"].idxmin(), "player"].value_counts()
max_points = melted.groupby("player")["points"].max()
min_points = melted.groupby("player")["points"].min()
average_points = melted.groupby("player")["points"].mean()
median_points = melted.groupby("player")["points"].median()

# Display some stats (wins, max, min, ...)
print("Number of Wins (Lowest Score per Round):")
print(wins)
print("\nMax Points per Player:")
print(max_points)
print("\nMin Points per Player:")
print(min_points)
print("\nAverage Points per Player:")
print(average_points)
print("\nMedian Points per Player:")
print(median_points)

# --- 1. Bar plot with mean & std ---
stats = melted.groupby("player")["points"].agg(["mean", "std"])

plt.figure()
stats["mean"].plot(kind="bar", yerr=stats["std"], capsize=4, rot=0)
plt.title("Average Scores with Standard Deviation")
plt.xlabel("Player")
plt.ylabel("Points")
plt.tight_layout()
plt.savefig("plots/average_scores.png")

# --- 2. Box plot of score distributions ---
plt.figure(figsize=(8, 6))
ax = sns.boxplot(data=melted, x="player", y="points", hue="player", palette="Set2", legend=False)
plt.title("Score Distribution per Player", fontsize=14, fontweight="bold")
plt.xlabel("Player", fontsize=12)
plt.ylabel("Points", fontsize=12)
plt.tight_layout()
plt.savefig("plots/score_distribution.png")

# --- 3. Violin plot
plt.figure(figsize=(8, 5))
sns.violinplot(x="player", y="points", data=melted, inner="quartile")
plt.title("Score Distributions per Player (Violin Plot)")
plt.ylabel("Points")
plt.xlabel("Player")
plt.tight_layout()
plt.savefig("plots/score_distribution_violin.png")

# --- 4. Heatmap of scores by game and player ---
# Aggregate by mean in case there are duplicate game_id/player combinations
heatmap_data = melted.groupby(["game_id", "player"])["points"].mean().unstack()

plt.figure(figsize=(8, 6))
sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu")
plt.title("Heatmap of Scores by Game and Player")
plt.xlabel("Player")
plt.ylabel("Game ID")
plt.tight_layout()
plt.savefig("plots/heatmap_scores.png")

# --- 5. Scatter plot of mean vs std ---
plt.figure(figsize=(8, 6))
sns.scatterplot(x="mean", y="std", data=stats, s=100)

for player in stats.index:
    plt.text(
        stats.loc[player, "mean"],
        stats.loc[player, "std"],
        player,
        horizontalalignment="left",
        size="medium",
        color="black",
        weight="semibold",
    )

plt.title("Player Consistency (Mean vs Std)")
plt.xlabel("Mean Score")
plt.ylabel("Standard Deviation")
plt.tight_layout()
plt.savefig("plots/mean_std_scatter.png")
