import csv
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

#load data



HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

time.sleep(1.0)

BASE = "https://www.saa.gov.uk"

search_term = list()
def build_search_url(search_term):
    """
    Build the simplest SAA search URL that returns the full result list.
    """
    params = {
        "SEARCHED": "1",
        "SEARCH_TABLE": "valuation_roll",
        "SEARCH_TERM": search_term,
        "searchtype": "listing"
    }
    qs = urllib.parse.urlencode(params)
    return f"{BASE}/search/?{qs}#results"

def parse_results_page(url):
    """
    Scrape the main search results page.
    Returns a list of dicts, one per property row.
    """
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("Error loading:", url)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    # TODO: Update this selector based on actual SAA HTML
    table = soup.find("table")
    if not table:
        print("No results table found:", url)
        return []

    properties = []
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        address = cols[0].get_text(strip=True)
        value = cols[1].get_text(strip=True)

        # Extract the link to detail page
        a = cols[0].find("a")
        detail_url = None
        if a and "href" in a.attrs:
            href = a["href"]
            if href.startswith("/"):
                detail_url = BASE + href
            else:
                detail_url = href

        properties.append({
            "result_address": address,
            "result_value": value,
            "detail_url": detail_url,
            "search_url": url
        })

    return properties

# set up session
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
                       

def parse_detail_page(url, max_retries=5):
    """
    Scrape a Scottish Assessors property detail page using div-based layout.
    Returns:
        - Property Address
        - Proprietor
        - Tenant
        - Rateable Value
        - detail_url
    """
    if not url:
        return {}

    data = {}
    keys_to_extract = ["Property Address", "Proprietor", "Tenant", "Occupier", "Rateable Value"]

    for attempt in range(max_retries):
        r = session.get(url)
        if r.status_code == 200:
            break
        elif r.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"429 received. Waiting {wait}s before retrying {url}...")
            time.sleep(wait)
        else:
            print(f"Error {r.status_code} fetching {url}")
            return {}
    else:
        print(f"Failed to fetch {url} after {max_retries} retries.")
        return {}

    soup = BeautifulSoup(r.text, "html.parser")

    # Loop over div rows
    for row in soup.find_all("div", class_="row table-row"):
        header_div = row.find("div", class_="header")
        value_div = row.find_all("div", class_="cell")
        if header_div and value_div:
            key = header_div.get_text(strip=True)
            # The value is the non-header cell
            val = next((v.get_text(strip=True) for v in value_div if "header" not in v.get("class", [])), "")
            if key in keys_to_extract:
                data[key] = val

    # Ensure all keys exist
    for k in keys_to_extract:
        data.setdefault(k, "")

    data["detail_url"] = url
    return data

#set up data
import csv

print("imported")

def main():
    input_csv = "EPCInput4b.csv"
    output_csv = "EPCDraft4b.csv"

    # Columns we want to save
    desired_columns = [
        "input_postcode",
        "input_address",
        "heating_type",
        "building_emissions",
        "result_address",
        "result_value",
        "Property Address",
        "Proprietor",
        "Tenant",
        "Rateable Value",
        "detail_url",
        "search_url",
        'ADDRESS1',
        'ADDRESS2',
        'POST_TOWN',
        'POSTCODE',
        'search_term',
        'PROPERTY_TYPE',
        'PROPERTY_TYPE_SHORT',
        'FLOOR_AREA',
        'CURRENT_ENERGY_PERFORMANCE_RATING',
        'CURRENT_ENERGY_PERFORMANCE_BAND',
        'MAIN_HEATING_FUEL',
        'ELECTRICITY_SOURCE',
        'RENEWABLE_SOURCES',
        'BUILDING_ENVIRONMENT',
        'BUILDING_EMISSIONS',
        'Demand KWH',
        'Demand MWH',
        'Demand GWH'
    ]

    all_rows = []

    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            address1 = row.get("ADDRESS1", "").strip()
            address2 = row.get("ADDRESS2", "").strip()
            post_town = row.get("POST_TOWN", "").strip()
            postcode = row.get("POSTCODE", "").strip()

            property_type_short = row.get("PROPERTY_TYPE_SHORT", "").strip()
            property_type = row.get("PROPERTY_TYPE", "").strip()
            floor_area = row.get("FLOOR_AREA", "").strip()

            energy_rating = row.get("CURRENT_ENERGY_PERFORMANCE_RATING", "").strip()
            energy_band = row.get("CURRENT_ENERGY_PERFORMANCE_BAND", "").strip()

            building_emissions = row.get("BUILDING_EMISSIONS", "").strip()
            renewable_sources = row.get("RENEWABLE_SOURCES", "").strip()
            electricity_source = row.get("ELECTRICITY_SOURCE", "").strip()
            main_heating_fuel = row.get("MAIN_HEATING_FUEL", "").strip()
            building_environment = row.get("BUILDING_ENVIRONMENT", "").strip()

            demand_kwh = row.get("Demand KWH", "").strip()
            demand_mwh = row.get("Demand MWH", "").strip()
            demand_gwh = row.get("Demand GWH", "").strip()
            term = f"{address1 or ''} {address2 or ''}".strip()
            
            search_url = build_search_url(term)
            results = parse_results_page(search_url)

            for r in results:
                detail_data = parse_detail_page(r["detail_url"])

                # Combine search result + detail data
                combined = {
                    "ADDRESS1": address1,
                    "ADDRESS2": address2,
                    "POST_TOWN": post_town,
                    "POSTCODE": postcode,
                    "PROPERTY_TYPE_SHORT": property_type_short,
                    "PROPERTY_TYPE": property_type,
                    "FLOOR_AREA": floor_area,
                    "CURRENT_ENERGY_PERFORMANCE_RATING": energy_rating,
                    "CURRENT_ENERGY_PERFORMANCE_BAND": energy_band,
                    "BUILDING_EMISSIONS": building_emissions,
                    "RENEWABLE_SOURCES": renewable_sources,
                    "ELECTRICITY_SOURCE": electricity_source,
                    "MAIN_HEATING_FUEL": main_heating_fuel,
                    "BUILDING_ENVIRONMENT": building_environment,
                    "Demand KWH": demand_kwh,
                    "Demand MWH": demand_mwh,
                    "Demand GWH": demand_gwh,
                    "search_term": term,
                    "search_url": r.get("search_url", ""),

                    # Search result data
                    "result_address": r.get("result_address", ""),
                    "result_value": r.get("result_value", ""),
                    "detail_url": r.get("detail_url", ""),

                    # Detail page data
                    "Property Address": detail_data.get("Property Address", ""),
                    "Proprietor": detail_data.get("Proprietor", ""),
                    "Tenant": detail_data.get("Tenant", ""),
                    "Rateable Value": detail_data.get("Rateable Value", "")
                }   

                all_rows.append(combined)
                print(f"Done with search term: {term}")
                time.sleep(5)  # polite delay

            time.sleep(5)

    if not all_rows:
        print("No records scraped.")
        return

    # Save clean output
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=desired_columns)
        writer.writeheader()
        writer.writerows(all_rows)

    print("Scraping complete:", len(all_rows), "properties extracted.")


main()
print("done")