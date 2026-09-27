'''import pandas as pd
import numpy as np
import pylahman

# 1. Load your existing dataset
file_path = 'the_baseball_scholar_mlb_player_stats_1901_present_csv.csv'
df = pd.read_csv(file_path, dtype=str)

# 2. Fetch Team Data from the local pylahman package
print("Loading local Lahman database...")

# Pull the people, batting, and pitching tables directly from the package
people = pylahman.People()[['playerID', 'bbrefID']]
batting = pylahman.Batting()[['playerID', 'yearID', 'teamID']]
pitching = pylahman.Pitching()[['playerID', 'yearID', 'teamID']]

# Combine batting and pitching, then drop duplicates
team_data = pd.concat([batting, pitching]).drop_duplicates()

# Map the bbrefID to the stats
team_data = pd.merge(team_data, people, on='playerID', how='inner')

# Handle Traded Players (If a player played for 2 teams in a year, combine them like "NYA/KCA")
team_data = team_data.groupby(['bbrefID', 'yearID'])['teamID'].apply(lambda x: '/'.join(x.unique())).reset_index()

# Rename columns to match your dataset for a clean merge
team_data = team_data.rename(columns={
    'bbrefID': 'bbref_player_id', 
    'yearID': 'season', 
    'teamID': 'team'
})

# Convert merge keys to strings to ensure they match perfectly
team_data['bbref_player_id'] = team_data['bbref_player_id'].astype(str)
team_data['season'] = team_data['season'].astype(str)

# 3. Merge the Team column into your dataset
print("Merging team data...")
df = pd.merge(df, team_data, on=['bbref_player_id', 'season'], how='left')

# 4. Apply previous normalizations
df['primary_position'] = df['primary_position'].fillna('UNKNOWN').str.upper()
df['primary_position'] = df['primary_position'].replace({'SP': 'P', 'RP': 'P'})

# Fill in a default team for anyone missing
df['team'] = df['team'].fillna('TOT') 

df = df.replace('#DIV/0!', np.nan)

int_columns = ['g', 'pa', 'ab', 'r', 'h', '1b', '2b', '3b', 'hr', 'rbi', 'sb', 'cs', 'bb', 'so', 'ibb', 'hbp', 'sf', 'sh', 'gdp', 'w', 'l', 'g.1', 'gs', 'cg', 'sho', 'sv', 'h.1', 'er', 'r.1', 'hr.1', 'bb.1', 'so.1', 'ibb.1', 'wp', 'hbp.1', 'bk', 'tbf']
for col in int_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

float_columns = ['wRC+', 'era-', 'era', 'ip', 'whip', 'war']
for col in float_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 5. Save the updated dataset
output_file = 'normalized_mlb_player_stats_with_teams.csv'
df.to_csv(output_file, index=False)
print(f"File saved successfully as: {output_file}")
'''
import pandas as pd

print("Downloading Chadwick ID Register parts (this will take a moment)...")

# 1. Fetch all 16 files from the new Chadwick structure and combine them
hex_chars = '0123456789abcdef'
dfs = []

for char in hex_chars:
    url = f"https://raw.githubusercontent.com/chadwickbureau/register/master/data/people-{char}.csv"
    try:
        # We only need the Baseball-Reference key and the MLBAM key
        temp_df = pd.read_csv(url, dtype=str)[['key_bbref', 'key_mlbam']]
        dfs.append(temp_df)
        print(f"Loaded part {char}/f...")
    except Exception as e:
        print(f"Failed to load part {char}: {e}")

# Combine all 16 pieces into one master lookup table
chadwick_df = pd.concat(dfs, ignore_index=True)

# Drop rows that are missing IDs (we can't fetch photos for them anyway)
chadwick_df = chadwick_df.dropna(subset=['key_mlbam', 'key_bbref'])

# 2. Rename columns for the merge
chadwick_df = chadwick_df.rename(columns={'key_bbref': 'bbref_player_id', 'key_mlbam': 'mlbam_id'})

# 3. Load your current normalized dataset
print("Loading player stats...")
df = pd.read_csv('normalized_mlb_player_stats_with_teams.csv', dtype=str)

# 4. Merge the MLBAM ID into your stats dataset
print("Merging IDs into dataset...")
df = pd.merge(df, chadwick_df, on='bbref_player_id', how='left')

# 5. Save the final file
df.to_csv('normalized_mlb_player_stats_with_images.csv', index=False)
print("Saved successfully! You now have MLBAM IDs for headshots.")