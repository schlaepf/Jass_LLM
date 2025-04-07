import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv("game_stats.csv")

melted = pd.concat([
    df[['game_id', 'round', 'name_player1', 'points_player1']]
    .rename(columns={'name_player1': 'player', 'points_player1': 'points'}),
    df[['game_id', 'round', 'name_player2', 'points_player2']]
    .rename(columns={'name_player2': 'player', 'points_player2': 'points'}),
    df[['game_id', 'round', 'name_player3', 'points_player3']]
    .rename(columns={'name_player3': 'player', 'points_player3': 'points'}),
    df[['game_id', 'round', 'name_player4', 'points_player4']]
    .rename(columns={'name_player4': 'player', 'points_player4': 'points'}),
], ignore_index=True)

wins = melted.loc[melted.groupby('game_id')['points'].idxmin(), 'player'].value_counts()

# Display win counts clearly
print("Number of Wins (Lowest Score per Round):")
print(wins)

# --- 1. Bar plot with mean & std ---
stats = melted.groupby('player')['points'].agg(['mean', 'std'])

plt.figure()
stats['mean'].plot(kind='bar', yerr=stats['std'], capsize=4, rot=0)
plt.title("Average Scores with Standard Deviation")
plt.xlabel("Player")
plt.ylabel("Points")
plt.tight_layout()
plt.savefig("average_scores.png")

# --- 2. Box plot of score distributions ---
plt.figure()
melted.boxplot(column='points', by='player', grid=False)
plt.title("Score Distribution per Player")
plt.suptitle("")  # Remove default boxplot suptitle
plt.xlabel("Player")
plt.ylabel("Points")
plt.tight_layout()
plt.savefig("score_distribution.png")

# --- 3. Violin plot
plt.figure(figsize=(8,5))
sns.violinplot(x='player', y='points', data=melted, inner='quartile')
plt.title('Score Distributions per Player (Violin Plot)')
plt.ylabel('Points')
plt.xlabel('Player')
plt.tight_layout()
plt.savefig("score_distribution_violin.png")

# --- 4. Heatmap of scores by game and player ---
heatmap_data = melted.pivot(index='game_id', columns='player', values='points')

plt.figure(figsize=(8,6))
sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu')
plt.title('Heatmap of Scores by Game and Player')
plt.xlabel('Player')
plt.ylabel('Game ID')
plt.tight_layout()
plt.savefig("heatmap_scores.png")

# --- 5. Scatter plot of mean vs std ---
plt.figure(figsize=(8,6))
sns.scatterplot(x='mean', y='std', data=stats, s=100)

for player in stats.index:
    plt.text(stats.loc[player,'mean'], stats.loc[player,'std'], player, 
             horizontalalignment='left', size='medium', color='black', weight='semibold')

plt.title('Player Consistency (Mean vs Std)')
plt.xlabel('Mean Score')
plt.ylabel('Standard Deviation')
plt.tight_layout()
plt.savefig("mean_std_scatter.png")
