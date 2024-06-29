from bs4 import BeautifulSoup
import pprint
import re

def clean_year_text(year):
    """Cleans the year string to ensure it can be parsed as an integer. Removes extra whitespace and newline characters."""
    return re.sub(r'\D', '', year)

def clean_label_text(label):
    """Cleans the label string to remove extra whitespace and newline characters."""
    return label.strip()

def clean_value_text(value):
    """Cleans the value string to remove extra whitespace, newline characters, and specific symbols like `€` and `.`."""
    # Remove newline characters and specific symbols, then strip leading/trailing spaces
    value = value.replace('\n', '').replace('\\n', '').replace('.', '').replace('€', '').strip()
    # Remove remaining extra whitespaces between numbers/text
    value = re.sub(r'\s+', ' ', value)
    return value

try:
    # Load the HTML content (assuming it is saved locally)
    with open('companyweb.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Extract the years dynamically
    header_cells = soup.select('thead tr.title-tab th[colspan="2"]')
    years = [clean_year_text(cell.get_text(strip=True)) for cell in header_cells]

    # Debugging: print extracted years
    #print(f"Extracted years: {years}")

    # Initialize dictionary to store financial data
    financial_data = {'jaarrekeningen': []}

    # Locate the financial data rows
    rows = soup.select('table.kerncijfers tbody tr')

    # Iterate over each row to extract the data
    for row in rows:
        cells = row.find_all(['td', 'th'])
        label = clean_label_text(cells[0].text)

        # Debugging: print extracted label
        #print(f"Processing label: {label}")

        for i, year in enumerate(years):
            if not year.isdigit():
                #print(f"Skipping invalid year value: {year}")
                continue  # Skip invalid year values

            cleaned_year = int(year)  # Converted to an integer

            index = 1 + 2 * i
            value = clean_value_text(cells[index].text) if index < len(cells) else None
            change = clean_value_text(cells[index + 1].text) if index + 1 < len(cells) else None

            # Debugging: print extracted value and change for each year
            #print(f"Year: {cleaned_year}, Value: {value}, Change: {change}")

            if value:
                # Find the year dictionary or create it
                year_dict = next((item for item in financial_data['jaarrekeningen'] if item.get('jaar') == cleaned_year), None)
                if not year_dict:
                    year_dict = {'jaar': cleaned_year}
                    financial_data['jaarrekeningen'].append(year_dict)

                # Add the financial data to the year dictionary
                if "Omzet" in label:
                    year_dict['omzet'] = value
                    year_dict['percentage_verandering_omzet'] = change
                elif "Winst/Verlies" in label:
                    year_dict['winst_verlies'] = value
                    year_dict['percentage_verandering_winst'] = change
                elif "Eigen vermogen" in label:
                    year_dict['eigen_vermogen'] = value
                    year_dict['percentage_verandering_vermogen'] = change
                elif "Brutomarge" in label:
                    year_dict['brutomarge'] = value
                    year_dict['percentage_verandering_brutomarge'] = change
                elif "Personeel" in label:
                    year_dict['personeel'] = value
                    year_dict['percentage_verandering_personeel'] = change

    # Print the extracted financial data
    pprint.pprint(financial_data)

except Exception as e:
    print(f"An error occurred: {e}")
