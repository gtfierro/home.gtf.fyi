.PHONY: all clean discogs

all: papers discogs clean
	./deploy.sh

serve: papers discogs
	hugo serve
	
papers: clean
	#cd publications && csvs-to-sqlite papers.csv papers.db
	cd publications && uv run buildpapersyml.py
	cd publications && uv run compile-papers.py > ../content/papers.md
	cd publications && sqlite3 papers.db < export-json.sql > ../static/papers.json

discogs:
	cd discogs && uv run generate_html.py
	cd discogs && uv run generate_genre_html.py
	mkdir -p static/albums
	cp discogs/genre.html static/albums/index.html

discogs/records.json: 
	cd discogs && uv run generate_json.py



clean:
	#cd publications && rm -f papers.db
