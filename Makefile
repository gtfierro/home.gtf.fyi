.PHONY: all clean

all: papers clean
	./deploy.sh
	
papers: clean
	#cd publications && csvs-to-sqlite papers.csv papers.db
	cd publications && python compile-papers.py > ../content/papers.md

clean:
	#cd publications && rm -f papers.db
