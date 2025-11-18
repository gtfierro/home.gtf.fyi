-- https://duckdb.org/docs/stable/core_extensions/vss#index-options
create table wiki(label text, abstract text, embedding float[384]);
insert into wiki select * from 'http://files.gtf.fyi/wiki-embeddings.parquet';

INSTALL vss;
LOAD vss;
CREATE INDEX my_hnsw_index ON wiki
USING HNSW (embedding)
WITH (metric = 'cosine', M=2);


CREATE MACRO lookup(q, k) AS TABLE
SELECT * FROM wiki
ORDER BY array_distance(embedding, q)
LIMIT k;

-- FROM lookup(<array>, k);
