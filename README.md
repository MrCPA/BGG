Here’s a **README** for your repository that explains how to use your script, its features, and requirements:

---

# BGG Data Processor & Report Generator

This project is a command-line tool designed to fetch, process, and generate reports for a user's board game collection and play data from **BoardGameGeek (BGG)**. It provides functionality to create individual PDF reports for each game category or output the data as a CSV.

## Features

- Fetches **collection** and **plays** data from the BoardGameGeek API for a specific user.
- Merges collection data with play history and categories.
- Updates or creates a categories CSV file to classify games by category.
- Generates **PDF reports** for each game category, showing the game name and the last date it was played.
- Optionally exports the processed data as a **CSV** file.

## Requirements

Make sure you have the following installed:

- Python 3.x
- Libraries:
  - `requests`
  - `pandas`
  - `reportlab`

You can install the required Python libraries by running:
```bash
pip install requests pandas reportlab
```

## How to Use

### Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/bgg-report-generator.git
cd bgg-report-generator
```

### Commands

The script provides three main commands: `fetch_data`, `process_data`, and `generate_report`. Each command performs a specific task and can be run from the command line.

1. **Fetch Data**  
   Fetch the collection and plays data for a specific user from the BoardGameGeek API.
   
   ```bash
   python combined_bgg_script.py fetch_data --username your_bgg_username
   ```

   This will save the collection and plays data as XML files in the `userdata/` directory.

2. **Process Data**  
   Process the collection and plays data, merge them with the categories, and save the result as `games_last_played.csv`.

   ```bash
   python combined_bgg_script.py process_data
   ```

   This will parse the XML files and generate an updated CSV with the games' last played dates and categories.

3. **Generate Report**  
   Generate a PDF report for each category or export all data to a CSV file.
   
   - **Generate PDF Reports**:
   
     ```bash
     python combined_bgg_script.py generate_report --output pdf
     ```

     This will create individual PDF files for each category in the `userdata/` directory.

   - **Export CSV**:
   
     ```bash
     python combined_bgg_script.py generate_report --output csv
     ```

     This will export the combined data into a single CSV file, `games_report_by_category.csv`.

## Directory Structure

The key files in the repository are as follows:

```
bgg-report-generator/
├── combined_bgg_script.py      # Main script with fetch, process, and report generation
├── userdata/                   # Directory where data and reports are saved
│   ├── collection.xml          # Fetched BGG collection data (XML)
│   ├── plays.xml               # Fetched BGG plays data (XML)
│   ├── game_categories.csv     # Categories for games
│   ├── games_last_played.csv   # Processed data with last played dates and categories
│   └── games_report_*.pdf      # Individual PDF reports by category
```

## Example Usage

To generate reports for your BGG collection and play history, follow these steps:

1. Fetch data:
   ```bash
   python combined_bgg_script.py fetch_data --username your_bgg_username
   ```

2. Process the fetched data:
   ```bash
   python combined_bgg_script.py process_data
   ```

3. Generate PDF reports by category:
   ```bash
   python combined_bgg_script.py generate_report --output pdf
   ```

Alternatively, you can generate a CSV of all data:
```bash
python combined_bgg_script.py generate_report --output csv
```

## Error Handling

- The script checks for missing files and handles network errors when fetching data from BGG.
- If XML files are missing or invalid, appropriate error messages will be shown, and the script will exit gracefully.

## Contributing

Feel free to fork the project, make changes, and submit a pull request. Contributions are welcome!

---

This README provides clear instructions on setting up and running the script, along with descriptions of the features and usage. Let me know if you'd like any additional details or sections!