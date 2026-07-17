-- Exports the papers table as a JSON array, with the comma-separated
-- "authors" column broken out into a proper JSON list of strings.
-- Usage: sqlite3 papers.db < export-json.sql > ../static/papers.json

.mode list

WITH RECURSIVE split_authors(id, rest, author) AS (
  SELECT rowid, authors || ',', NULL
  FROM papers
  UNION ALL
  SELECT id,
         substr(rest, instr(rest, ',') + 1),
         trim(substr(rest, 1, instr(rest, ',') - 1))
  FROM split_authors
  WHERE rest <> ''
),
authors_list AS (
  SELECT id, author
  FROM split_authors
  WHERE author IS NOT NULL AND author <> ''
),
papers_json AS (
  SELECT
    p.rowid AS id,
    p.type,
    p.title,
    p.pdf,
    p.link,
    p.slides,
    p.conference,
    p.location,
    p.month,
    p.year,
    p.award,
    p.repo,
    (
      SELECT json_group_array(a.author)
      FROM authors_list a
      WHERE a.id = p.rowid
    ) AS authors
  FROM papers p
)
SELECT json_group_array(
  json_object(
    'type', type,
    'title', title,
    'pdf', pdf,
    'link', link,
    'slides', slides,
    'authors', json(authors),
    'conference', conference,
    'location', location,
    'month', month,
    'year', year,
    'award', award,
    'repo', repo
  )
)
FROM (
  SELECT * FROM papers_json ORDER BY year DESC, id DESC
);
