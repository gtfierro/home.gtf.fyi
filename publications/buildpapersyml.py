# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///

import sqlite3
import yaml

def fetch_papers_from_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('papers.db')  # replace 'papers.db' with your database file
    cursor = conn.cursor()

    # Fetch all paper records
    cursor.execute("SELECT type, title, pdf, link, slides, authors, conference, location, month, year, award FROM papers")
    papers = cursor.fetchall()

    # Close the database connection
    conn.close()

    return papers

def papers_to_yaml(papers):
    data = []
    for paper in papers:
        data.append({
            'type': paper[0],
            'title': paper[1],
            'pdf': paper[2],
            'link': paper[3],
            'slides': paper[4],
            'authors': paper[5],
            'conference': paper[6],
            'location': paper[7],
            'month': paper[8],
            'year': paper[9],
            'award': paper[10]
        })

    # Convert the list of papers to YAML
    yaml_data = yaml.dump(data, default_flow_style=False)
    return yaml_data

def write_yaml_to_file(yaml_data, file_path):
    with open(file_path, 'w') as file:
        file.write(yaml_data)

def main():
    # Fetch papers from the database
    papers = fetch_papers_from_db()

    # Convert the papers to YAML format
    yaml_data = papers_to_yaml(papers)

    # Define the path where the YAML file will be saved in your Hugo site's data directory
    file_path = '../data/papers.yaml'  # modify this path as needed

    # Write the YAML data to a file
    write_yaml_to_file(yaml_data, file_path)
    print(f"Paper data has been written to {file_path}")

if __name__ == '__main__':
    main()
