.PHONY: all clean

all: papers clean
	./deploy.sh
	
papers: clean
	#cd publications && csvs-to-sqlite papers.csv papers.db
	cd publications && uv run buildpapersyml.py
	cd publications && uv run compile-papers.py > ../content/papers.md

clean:
	#cd publications && rm -f papers.db
