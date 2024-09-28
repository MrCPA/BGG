import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import os

def parse_collection_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    data = []
    for item in root.findall('.//item'):
        game_id = item.get('objectid')
        name = item.find('.//name').text
        data.append({'game_id': str(game_id), 'name': name})
    
    df = pd.DataFrame(data)
    print(f"Parsed {len(df)} games from XML")
    return df

def parse_plays_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    data = []
    for play in root.findall('.//play'):
        game_id = play.find('.//item').get('objectid')
        date = play.get('date')
        data.append({'game_id': game_id, 'date': date})
    
    return pd.DataFrame(data)

def update_categories_file(collection_df, categories_file):
    # Ensure game_id is string type in collection_df
    collection_df['game_id'] = collection_df['game_id'].astype(str)

    if os.path.exists(categories_file):
        # Read existing categories
        categories_df = pd.read_csv(categories_file)
        
        # Ensure game_id is string type in categories_df
        categories_df['game_id'] = categories_df['game_id'].astype(str)
        
        # Identify new games
        new_games = collection_df[~collection_df['game_id'].isin(categories_df['game_id'])]
        
        print(f"Total games in collection: {len(collection_df)}")
        print(f"Games in existing categories file: {len(categories_df)}")
        print(f"New games identified: {len(new_games)}")
        
        if not new_games.empty:
            # Add new games to categories dataframe
            new_categories = new_games[['game_id', 'name']].copy()
            new_categories['category'] = ''
            categories_df = pd.concat([categories_df, new_categories], ignore_index=True)
            
            # Save updated categories
            categories_df.to_csv(categories_file, index=False)
            print(f"Categories file updated with {len(new_games)} new games: {categories_file}")
        else:
            print("No new games to add to categories file.")
    else:
        # If file doesn't exist, create it with all games
        categories_df = collection_df[['game_id', 'name']].copy()
        categories_df['category'] = ''
        categories_df.to_csv(categories_file, index=False)
        print(f"New categories file created with {len(categories_df)} games: {categories_file}")
    
    return categories_df

def merge_categories(result_df, categories_df):
    return pd.merge(result_df, categories_df[['game_id', 'category']], on='game_id', how='left')

def main():
    # Parse XML files
    collection_df = parse_collection_xml('./userdata/collection_mark4.xml')
    plays_df = parse_plays_xml('./userdata/plays_mark4.xml')
    
    # Update categories file and get current categories
    categories_df = update_categories_file(collection_df, './userdata/game_categories.csv')
    
    # Get the last play date for each game
    last_plays = plays_df.sort_values('date').groupby('game_id').last().reset_index()
    
    # Merge collection and play data
    result = pd.merge(collection_df, last_plays, on='game_id', how='left')
    
    # Merge with categories
    result = merge_categories(result, categories_df)
    
    # Sort by last played date (most recent first)
    result = result.sort_values('date', ascending=False)
    
    # Format the date and handle games never played
    result['last_played'] = pd.to_datetime(result['date']).dt.strftime('%Y-%m-%d')
    result['last_played'] = result['last_played'].fillna('0')

    result = result.sort_values(by=['category','last_played'], ascending=[True,True])

    # Select and rename columns for final output
    final_df = result[['name', 'last_played', 'category']].rename(columns={
        'name': 'Game Name', 
        'category': 'Category',
        'last_played': 'Last Played Date'
    })

    # Save to CSV
    final_df.to_csv('./userdata/games_last_played.csv', index=False)
    print("CSV file created: ./userdata/games_last_played.csv")

if __name__ == "__main__":
    main()