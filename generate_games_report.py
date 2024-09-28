
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import pandas as pd

# Load the CSV data
def load_data(csv_file):
    return pd.read_csv(csv_file)

# Generate the PDF report by category
def generate_pdf_report(data, output_path):
    # Custom paragraph style for word wrapping
    game_name_style_wrapped = ParagraphStyle(name="GameNameStyleWrapped", fontSize=10)
    
    # Create the PDF document
    pdf = SimpleDocTemplate(output_path, pagesize=A4)
    content = []
    
    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("Games Report by Category", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 0.25 * inch))

    # Group the data by category
    grouped_games = data.groupby("Category")
    
    # Add each category and its games in a table format
    for category, games in grouped_games:
        # Category header
        category_header = Paragraph(f"<b>{category}</b>", styles['Heading2'])
        content.append(category_header)
        
        # Prepare data for the table: headers and rows for games and last played dates
        table_data = [["Game Name", "Last Played"]]
        
        for _, row in games.iterrows():
            game_name = row['Game Name']
            last_played = row['Last Played Date']
            table_data.append([Paragraph(game_name, game_name_style_wrapped), last_played])
        
        # Create a table with the game data
        table = Table(table_data, colWidths=[4.5 * inch, 1.5 * inch])
        
        # Apply table styling for readability and word wrapping
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),  # Ensure word wrapping
        ]))
        
        # Add the table to the content
        content.append(table)
        content.append(Spacer(1, 0.5 * inch))

    # Build the PDF
    pdf.build(content)

# Main function
if __name__ == "__main__":
    # Path to CSV file and PDF output
    csv_file = "./userdata/games_last_played.csv"
    output_pdf = "games_report_by_category.pdf"
    
    # Load the data
    data = load_data(csv_file)
    
    # Generate the PDF report
    generate_pdf_report(data, output_pdf)
    print(f"PDF report generated: {output_pdf}")
