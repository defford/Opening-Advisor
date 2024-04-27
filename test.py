import berserk
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Lichess client
lichess_api = os.getenv('LICHESS_API')
session = berserk.TokenSession(lichess_api)
client = berserk.Client(session=session)

def fetch_games(client, username, num_games=1000):
    """Fetches the list of games for a given player."""
    try:
        return client.games.export_by_player(username, max=num_games, opening=True)
    except Exception as e:
        print(f"Failed to fetch games: {e}")
        return []

def prepare_dataframe(games, username):
    """Creates a DataFrame from the game data."""
    rows = []
    for game in games:
        try:
            opening = game.get('opening', {}).get('name', 'Unknown Opening')
            game_speed = game['speed']
            result = '0'  # Draw by default
            winner = game.get('winner')
            if winner and game['players'][winner]['user']['name'] == username:
                result = '1' if winner == 'white' else '-1'
            rows.append({
                'Opening': opening,
                'Game Speed': game_speed,
                'Result': result
            })
        except KeyError:
            continue

    return pd.DataFrame(rows)

def analyze_openings(df):
    """Analyzes openings to provide total plays, wins, and win percentages."""
    # Count total plays by specific openings
    opening_counts = df['Opening'].value_counts().rename('Total Plays')

    # Filter for wins and count by specific openings
    wins_df = df[df['Result'] != '0']
    opening_wins = wins_df['Opening'].value_counts().rename('Wins')

    # Combine wins and total plays into a single DataFrame
    summary_df = pd.DataFrame({'Total Plays': opening_counts, 'Wins': opening_wins})
    summary_df['Wins'].fillna(0, inplace=True)  # Replace NaN values with 0 for openings with no wins

    # Calculate win percentage
    summary_df['Win Percentage'] = (summary_df['Wins'] / summary_df['Total Plays'] * 100).round(2)

    return summary_df


def summarize_opening_families(df):
    """Groups openings by their families and calculates total plays, wins, and win percentages."""
    # Extract opening families by splitting the opening names and taking the first part
    df['Opening Family'] = df['Opening'].apply(lambda x: x.split(':')[0].split('|')[0].strip())
    
    # Count total plays by specific opening families
    family_counts = df['Opening Family'].value_counts().rename('Total Plays')
    
    # Filter for wins and count by specific opening families
    wins_df = df[df['Result'] != '0']
    family_wins = wins_df['Opening Family'].value_counts().rename('Wins')
    
    # Combine wins and total plays into a single DataFrame
    summary_family_df = pd.DataFrame({'Total Plays': family_counts, 'Wins': family_wins})
    summary_family_df['Wins'].fillna(0, inplace=True)  # Replace NaN values with 0 for families with no wins
    
    # Calculate win percentage
    summary_family_df['Win Percentage'] = (summary_family_df['Wins'] / summary_family_df['Total Plays'] * 100).round(2)
    
    return summary_family_df
# Main execution
username = 'rvvr4'
games = fetch_games(client, username)
df = prepare_dataframe(games, username)
opening_summary = analyze_openings(df)
opening_family_summary = summarize_opening_families(df)

print(opening_summary.sort_values(by='Wins', ascending=False))
print(opening_family_summary.sort_values(by='Wins', ascending=False))

