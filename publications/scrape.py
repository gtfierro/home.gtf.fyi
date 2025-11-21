# /// script
# dependencies = [
#     "requests"
# ]
# ///
import requests
import datetime

SQL_OUTPUT_FILE = "newpapers.sql"

def get_paper_metadata(doi):
    """
    Fetches metadata for a given DOI from the Crossref API.
    """
    base_url = f"https://api.crossref.org/works/{doi}"
    
    # polite pool: including a mailto header is good etiquette for Crossref
    headers = {
        "User-Agent": "PublicationPopulator/1.0 (mailto:your_email@example.com)"
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()['message']
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for DOI {doi}: {e}")
        return None

def parse_metadata(data, doi):
    """
    Extracts relevant fields from Crossref JSON response to match the database schema.
    """
    # 1. Title
    title_list = data.get('title', [])
    title = title_list[0] if title_list else "Unknown Title"

    # 2. Authors (format: "First Last, First Last")
    authors_list = data.get('author', [])
    authors_formatted = []
    for auth in authors_list:
        given = auth.get('given', '')
        family = auth.get('family', '')
        if given or family:
            authors_formatted.append(f"{given} {family}".strip())
    authors = ", ".join(authors_formatted)

    # 3. Conference / Journal Name
    # Crossref uses 'container-title' for the journal or conference proceedings name
    container_titles = data.get('container-title', [])
    conference = container_titles[0] if container_titles else ""
    
    # 4. Type (Infer "conference" or "journal" from Crossref type)
    raw_type = data.get('type', '')
    if 'proceedings' in raw_type or 'conference' in raw_type:
        paper_type = 'conference'
    elif 'journal' in raw_type:
        paper_type = 'journal'
    else:
        paper_type = 'other'

    # 5. Date (Year and Month)
    issued = data.get('issued', {}).get('date-parts', [[None, None]])[0]
    year = issued[0] if len(issued) > 0 else None
    month_num = issued[1] if len(issued) > 1 else None
    
    # Convert month number (e.g., 2) to name (e.g., "February")
    month = ""
    if month_num:
        try:
            month = datetime.date(1900, month_num, 1).strftime('%B')
        except ValueError:
            pass

    # 6. Location
    # Location is tricky in standard metadata. 
    # Sometimes it's in 'event' object, sometimes strictly publisher location.
    # We check for an event location specifically.
    location = ""
    if 'event' in data and 'location' in data['event']:
        location = data['event']['location']
    
    # 7. Link (URL)
    link = data.get('URL', f"https://doi.org/{doi}")

    # Return tuple matching the INSERT statement order (excluding PDF/Slides/Award)
    return {
        "type": paper_type,
        "title": title,
        "link": link,
        "authors": authors,
        "conference": conference,
        "location": location,
        "month": month,
        "year": year
    }

def sql_literal(value):
    """Return a SQL-safe literal for INSERT statements."""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def build_insert_statement(meta, pdf_name=""):
    """Create the INSERT statement for the papers table."""
    slides = None
    award = None

    columns = [
        "type",
        "title",
        "pdf",
        "link",
        "slides",
        "authors",
        "conference",
        "location",
        "month",
        "year",
        "award",
    ]

    values = [
        meta['type'],
        meta['title'],
        pdf_name,
        meta['link'],
        slides,
        meta['authors'],
        meta['conference'],
        meta['location'],
        meta['month'],
        meta['year'],
        award,
    ]

    columns_csv = ", ".join(columns)
    value_lines = []
    for idx, (column, value) in enumerate(zip(columns, values)):
        literal = sql_literal(value)
        comma = "," if idx < len(columns) - 1 else ""
        value_lines.append(f"    {literal}{comma} -- {column}")

    formatted_values = "\n".join(value_lines)
    return f"INSERT INTO papers ({columns_csv}) VALUES (\n{formatted_values}\n);"

def main():
    insert_statements = []

    # Example DOIs (You can replace this list or input via CLI)
    dois_to_add = [
            "10.1145/3736425.3770107",
            "10.1145/3736425.3770097",
            "10.1145/3736425.3772123",
            "10.1145/3736425.3772119",
    ]

    for doi in dois_to_add:
        print(f"Processing DOI: {doi}...")
        
        # 2. Fetch Data
        raw_data = get_paper_metadata(doi)
        
        if raw_data:
            # 3. Parse Data
            parsed_meta = parse_metadata(raw_data, doi)
            
            # 4. Insert (Assuming you have the PDF filename, otherwise passing empty string)
            # You can modify this logic to scan a folder and match DOIs if needed.
            pdf_filename = "" 
            insert_statements.append(build_insert_statement(parsed_meta, pdf_filename))

    if insert_statements:
        with open(SQL_OUTPUT_FILE, "w", encoding="utf-8") as sql_file:
            sql_file.write("\n".join(insert_statements) + "\n")
        print(f"Wrote {len(insert_statements)} insert statements to {SQL_OUTPUT_FILE}.")
    else:
        print("No insert statements generated.")

if __name__ == "__main__":
    main()
