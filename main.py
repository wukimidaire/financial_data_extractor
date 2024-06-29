from bs4 import BeautifulSoup
import re
import os
import json
from datetime import datetime

# Load the HTML content
file_path = 'companyweb.html'

# Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

with open(file_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Function to extract VAT number
def extract_vat_number(soup):
    vat_indicators = ['VAT number', 'btw', 'BTW-nummer', 'btw-nummer', 'btw nummer']
    vat_number_element = None

    for indicator in vat_indicators:
        vat_number_element = soup.find(text=lambda x: x and indicator in x)
        if vat_number_element:
            break

    if vat_number_element:
        vat_number = vat_number_element.find_next().text.strip()
        match = re.search(r'\b(BE\d{10})\b', vat_number)
        if match:
            return match.group(1)
    return None

# Extract the VAT number
vat_number = extract_vat_number(soup)

# Safely retrieve text of the next sibling element or return an empty string if not found
def safe_find_next_sibling(element, tag=None, class_=None):
    sibling = element.find_next_sibling(tag or "div", class_=class_) if element else None
    return sibling.text.strip() if sibling else ""

# Debugging helper to print elements
def debug_element(element, msg=""):
    if element:
        print(f"{msg}: {element}")
    else:
        print(f"{msg} not found")

# Safely extract text content based on tag and class
def safe_extract(soup, tag=None, text=None, class_=None, itemprop=None):
    element = soup.find(tag, text=text, class_=class_, itemprop=itemprop)
    debug_element(element, f"{text or itemprop} element")
    return element.text.strip() if element else ""

# Helper function to format dates
def format_date(date_str, input_format="%d-%m-%Y", output_format="%d/%m/%Y"):
    try:
        date_obj = datetime.strptime(date_str.strip(), input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str.strip()  # Return original string if parsing fails

# Extract the company information with checks and wider searches


address_element = soup.find("div", itemprop="address")
address = ''.join([text.strip() for text in address_element.stripped_strings]) if address_element else ""
debug_element(address, "Address")

founding_date_element = soup.find("div", itemprop="foundingDate")
founding_date = founding_date_element.text.strip() if founding_date_element else ""

# Format the "oprichting" date
formatted_founding_date = format_date(founding_date, input_format="%d-%m-%Y", output_format="%d/%m/%Y")

debug_element(founding_date_element, "Founding date")

main_activity = safe_extract(soup, tag="span", itemprop="description")

latest_report_date_element = soup.find("summary", text="Wanneer heeft Sioen Industries voor het laatst een jaarrekening neergelegd?")
latest_report_date = latest_report_date_element.find_next("div").text.strip() if latest_report_date_element else ""

nbb_link_element = soup.find("a", href=lambda href: href and 'consult.cbso.nbb.be' in href)
debug_element(nbb_link_element, "NBB Link element")
nbb_link = nbb_link_element['href'] if nbb_link_element else ""

# Expanding search for KBO and Staatsblad links
kbo_link_element = soup.find("a", text=lambda text: text and "KBO" in text)
debug_element(kbo_link_element, "KBO Link element")
kbo_link = kbo_link_element.get('href') if kbo_link_element else ""

staatsblad_link_element = soup.find("a", text=lambda text: text and "Staatsblad" in text)
debug_element(staatsblad_link_element, "Staatsblad Link element")
staatsblad_link = staatsblad_link_element.get('href') if staatsblad_link_element else ""

latest_revenue_element = soup.find("summary", text=lambda text: text and "Wat is de jaarlijkse omzet" in text)
debug_element(latest_revenue_element, "Latest Revenue element")
latest_revenue_text = latest_revenue_element.find_next("div").text.strip().replace("\n", " ").replace("\t", "") if latest_revenue_element else ""
latest_revenue = latest_revenue_text.split()[-1]

latest_fte_element = soup.find("summary", text=lambda text: text and "Hoeveel werknemers" in text)
debug_element(latest_fte_element, "Latest FTE element")
latest_fte_text = latest_fte_element.find_next("div").text.strip().replace("\n", " ").replace("\t", "") if latest_fte_element else ""
latest_fte = latest_fte_text.split()[1] if latest_fte_text else ""

# Extract financial years available in the table
years_elements = soup.find_all("th", text=True)
years = [int(year.text) for year in years_elements if year.text.isdigit() and len(year.text) == 4]

financial_data = []
for year in years:
    year_element = soup.find("th", text=str(year))
    omzet = safe_find_next_sibling(year_element)
    omzet_change = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[1].text.strip()
    winst_verlies = safe_find_next_sibling(year_element).find_next_sibling().text.strip()
    winst_change = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[3].text.strip()
    eigen_vermogen = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[4].text.strip()
    vermogen_change = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[5].text.strip()
    brutomarge = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[6].text.strip()
    marge_change = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[7].text.strip()
    personeel = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[8].text.strip()
    personeel_change = safe_find_next_sibling(year_element, tag=False, class_="financial-number ")[9].text.strip()

    financial_data.append({
        "jaar": year,
        "omzet": omzet,
        "percentage_verandering_omzet": omzet_change,
        "winst_verlies": winst_verlies,
        "percentage_verandering_winst": winst_change,
        "eigen_vermogen": eigen_vermogen,
        "percentage_verandering_vermogen": vermogen_change,
        "brutomarge": brutomarge,
        "percentage_verandering_brutomarge": marge_change,
        "personeel": personeel,
        "percentage_verandering_personeel": personeel_change
    })

# Compile all data
company_info = {
    "adres": address,
    "oprichting": formatted_founding_date,  # Use formatted date
    "hoofdactiviteit": main_activity,
    "jaarrekeningen": financial_data,
    "nbb": nbb_link,
    "kbo": kbo_link,
    "staatsblad": staatsblad_link,
    "laatst_neergelegde_jaarrekening": latest_report_date,
    "meest_recente_omzet": latest_revenue,
    "meest_recente_fte": latest_fte,
    "btw-nummer": vat_number  # Added VAT number
}

# Output the extracted data as JSON
with open('company_info.json', 'w', encoding='utf-8') as f:
    json.dump(company_info, f, ensure_ascii=False, indent=4)

print(json.dumps(company_info, ensure_ascii=False, indent=4))
