.PHONY: all clean discogs

all: papers discogs clean
	./deploy.sh
	
papers: clean
	#cd publications && csvs-to-sqlite papers.csv papers.db
	cd publications && uv run buildpapersyml.py
	cd publications && uv run compile-papers.py > ../content/papers.md

discogs:
	cd discogs && uv run generate_html.py
	cp discogs/index.html static/discogs.html

discogs/records.json: 
	cd discogs && uv run generate_json.py



clean:
	#cd publications && rm -f papers.db
