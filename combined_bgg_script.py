import argparse
import requests
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.etree import ElementTree as ET
from pathlib import Path
import time
import os

# Function to fetch data from BGG API
def get_bgg_data(endpoint, username, params=None):
    base_url = f"https://boardgamegeek.com/xmlapi2/{endpoint}"
    if params is None:
        params = {}
    params['username'] = username

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            return response.content
        elif response.status_code == 202:
            print(f"Request for {endpoint} accepted but still processing. Retrying after a short wait.")
            time.sleep(15)
            return get_bgg_data(endpoint, username, params)
        else:
            print(f"Error: Unable to fetch {endpoint} data. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to the BoardGameGeek API. Details: {e}")
        return None

# Save XML data to file
def save_to_file(data, filename):
    try:
        with open(filename, 'wb') as f:
            f.write(data)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error: Failed to save data to {filename}. Details: {e}")

# Fetch data from BGG and save as XML
def fetch_data(username):
    # Fetch collection data
    collection_data = get_bgg_data('collection', username, {'own': 1})
    if collection_data:
        save_to_file(collection_data, f"./userdata/collection.xml")
    else:
        print("Failed to retrieve collection data.")

    # Fetch plays data
    plays_data = get_bgg_data('plays', username)
    if plays_data:
        save_to_file(plays_data, f"./userdata/plays.xml")
    else:
        print("Failed to retrieve plays data.")
# Parse collection XML
def parse_collection_xml(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        data = []
        for item in root.findall('.//item'):
            game_id = item.get('objectid')
            name = item.find('.//name').text
            data.append({'game_id': game_id, 'name': name})

        return pd.DataFrame(data)
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML from {file_path}. Details: {e}")
        return None

# Parse plays XML
def parse_plays_xml(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        data = []
        for play in root.findall('.//play'):
            game_id = play.find('.//item').get('objectid')
            date = play.get('date')
            data.append({'game_id': game_id, 'last_played': date})

        return pd.DataFrame(data)
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML from {file_path}. Details: {e}")
        return None
# Update game categories CSV file
def update_categories_file(collection_df, categories_file):
    if collection_df is None:
        print("Error: Collection data is missing, cannot update categories.")
        return None

    collection_df['game_id'] = collection_df['game_id'].astype(str)

    # Check if the categories file exists
    if os.path.exists(categories_file):
        try:
            categories_df = pd.read_csv(categories_file)
            categories_df['game_id'] = categories_df['game_id'].astype(str)

            new_games = collection_df[~collection_df['game_id'].isin(categories_df['game_id'])]

            if not new_games.empty:
                new_categories = new_games[['game_id', 'name']].copy()
                new_categories['category'] = ''
                categories_df = pd.concat([categories_df, new_categories], ignore_index=True)
                categories_df.to_csv(categories_file, index=False)
                print(f"Categories file updated with {len(new_games)} new games.")
            else:
                print("No new games to add.")
        except Exception as e:
            print(f"Error: Failed to update {categories_file}. Details: {e}")
            return None
    else:
        # Create a new categories file if it doesn't exist
        try:
            collection_df[['game_id', 'name']].assign(category='').to_csv(categories_file, index=False)
            print(f"Categories file created with {len(collection_df)} games.")
        except Exception as e:
            print(f"Error: Failed to create categories file {categories_file}. Details: {e}")
            return None

    return pd.read_csv(categories_file)

# Merge collection and plays data
def merge_data(collection_df, plays_df, categories_df):
    if collection_df is None or plays_df is None or categories_df is None:
        print("Error: One or more dataframes are missing, cannot merge data.")
        return None

    # Ensure all game_id columns are strings
    collection_df['game_id'] = collection_df['game_id'].astype(str)
    plays_df['game_id'] = plays_df['game_id'].astype(str)
    categories_df['game_id'] = categories_df['game_id'].astype(str)

    # Get the last play date for each game
    last_plays = plays_df.sort_values('last_played').groupby('game_id').last().reset_index()

    # Merge collection with play data and categories
    result = pd.merge(collection_df, last_plays, on='game_id', how='left')
    result = pd.merge(result, categories_df[['game_id', 'category']], on='game_id', how='left')

    # Handle missing 'last_played' dates
    result['last_played'] = pd.to_datetime(result['last_played']).dt.strftime('%Y-%m-%d').fillna('0')

    return result.sort_values(by=['category', 'last_played'], ascending=[True, True])
# Generate PDF report for each category
def generate_pdf_report_by_category(data):
    if data is None:
        print("Error: No data available to generate reports.")
        return

    # Set up styles for the PDF
    styles = getSampleStyleSheet()
    styles['Normal'].fontSize = 10

    # Group games by category
    grouped_games = data.groupby("category")

    for category, games in grouped_games:
        # Prepare file name, replacing spaces or special characters in the category name
        sanitized_category = category.replace(" ", "_").replace("/", "_")
        output_pdf = f'./userdata/games_report_{sanitized_category}.pdf'

        try:
            # Create a new PDF for each category
            pdf = SimpleDocTemplate(
                output_pdf,
                pagesize=letter,
                leftMargin=0.5 * inch,
                rightMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch
            )

            content = []

            # Title for the category
            title = Paragraph(f"Games Report for Category: {category}", styles['Title'])
            content.append(title)
            content.append(Spacer(1, 0.5 * inch))

            # Table with game names and last played dates
            table_data = [["Game Name", "Last Played"]]
            for _, row in games.iterrows():
                table_data.append([Paragraph(row['name'], styles['Normal']), Paragraph(row['last_played'], styles['Normal'])])

            table = Table(table_data, colWidths=[5.0 * inch, 2.5 * inch])  # Adjust column widths for letter size
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            content.append(table)
            content.append(Spacer(1, 0.5 * inch))

            # Build the PDF document for this category
            pdf.build(content)
            print(f"PDF report generated for category: {category} -> {output_pdf}")
        except Exception as e:
            print(f"Error: Failed to generate PDF for category {category}. Details: {e}")

# Main function to process and handle commands
def main():
    parser = argparse.ArgumentParser(description="BGG Data Fetch, Processing, and Report Generation")
    subparsers = parser.add_subparsers(dest="command")

    # Fetch data command
    fetch_parser = subparsers.add_parser('fetch_data')
    fetch_parser.add_argument('--username', required=True, help="BGG username")

    # Process data command
    process_parser = subparsers.add_parser('process_data')

    # Generate report command
    report_parser = subparsers.add_parser('generate_report')
    report_parser.add_argument('--output', choices=['pdf', 'csv'], default='pdf', help="Output report format")

    args = parser.parse_args()

    if args.command == 'fetch_data':
        fetch_data(args.username)
    elif args.command == 'process_data':
        collection_df = parse_collection_xml('./userdata/collection.xml')
        plays_df = parse_plays_xml('./userdata/plays.xml')
        categories_df = update_categories_file(collection_df, './userdata/game_categories.csv')
        final_df = merge_data(collection_df, plays_df, categories_df)
        final_df.to_csv('./userdata/games_last_played.csv', index=False)
        print("Data processed and saved to games_last_played.csv")
    elif args.command == 'generate_report':
        data = pd.read_csv('./userdata/games_last_played.csv')
        if args.output == 'pdf':
            generate_pdf_report_by_category(data)
        elif args.output == 'csv':
            data.to_csv('games_report_by_category.csv', index=False)
            print("CSV report generated: games_report_by_category.csv")

if __name__ == "__main__":
    main()
