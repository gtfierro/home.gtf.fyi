# /// script
# dependencies = [
#   "jinja2",
# ]
# ///
import sys
import re
import jinja2
import sqlite3

def slugify(title):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title or '').strip('-').lower()
    return slug

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0].replace(' ','_')] = row[idx]
    return d

def month_to_number(month_name):
    months = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    return months.get(month_name, month_name)


# --- BibTeX generation -------------------------------------------------------

BIBTYPE = {
    'conference': 'inproceedings',
    'workshop': 'inproceedings',
    'demoposter': 'inproceedings',
    'journal': 'article',
    'misc': 'misc',
    'software': 'misc',
}

def _split_authors(raw):
    """Split a comma-separated author string into individual names. Some source
    rows bake ' and '/'&' into the comma-separated string; normalize those to
    commas first so every name stands alone (and the BibTeX ' and ' join is exact)."""
    raw = re.sub(r'\s*\band\b\s*', ', ', raw or '')
    raw = re.sub(r'\s+&\s+', ', ', raw)
    names = []
    for part in re.split(r'\s*,\s*', raw):
        part = part.strip().strip('.').strip()
        if part:
            names.append(part)
    return names

def _cite_key(authors, year, title):
    first = authors[0] if authors else 'anon'
    tokens = first.split()
    lastname = tokens[-1] if tokens else first
    words = re.findall(r'[A-Za-z0-9]+', title or '')
    word = words[0].lower() if words else 'untitled'
    return f"{lastname.lower()}{year or ''}{word}"

def bibtex_for(row):
    """Render a paper row (from the papers table) as a BibTeX entry string."""
    authors = _split_authors(row.get('authors') or '')
    year = row.get('year') or ''
    key = _cite_key(authors, year, row.get('title'))
    bibtype = BIBTYPE.get((row.get('type') or 'misc').lower(), 'misc')
    venue = (row.get('conference') or '').strip()

    # Theses: promote to @phdthesis/@mastersthesis and attach a school.
    SCHOOL = "University of California, Berkeley"
    if venue == "PhD Dissertation":
        bibtype = 'phdthesis'
    elif venue == "Masters Thesis":
        bibtype = 'mastersthesis'

    lines = [f"@{bibtype}{{{key},"]

    def add(field, val):
        val = (val or '').strip()
        if val:
            lines.append(f"  {field} = {{{val}}},")

    add('title', row.get('title'))
    add('author', ' and '.join(authors))
    if bibtype in ('phdthesis', 'mastersthesis'):
        add('school', SCHOOL)
    elif bibtype == 'article':
        add('journal', venue)
    elif bibtype == 'misc':
        add('howpublished', venue)
    else:
        add('booktitle', venue)
    add('address', row.get('location'))
    add('month', row.get('month'))
    add('year', str(year) if year else None)
    url = row.get('link') or (f"https://gtf.fyi/papers/{row['pdf']}" if row.get('pdf') else None)
    add('url', url)
    note_bits = []
    if row.get('award'):
        note_bits.append(row['award'])
    if row.get('repo'):
        note_bits.append(f"Repository: {row['repo']}")
    add('note', '; '.join(note_bits))

    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]
    lines.append("}")
    return '\n'.join(lines)


con = sqlite3.connect('papers.db')
con.row_factory = dict_factory
con.create_function('month_to_number', 1, month_to_number)
cur = con.cursor()

md_template = jinja2.Template("""
<div class="pub pub-{{ type }}" id="{{ slug }}">

**{{ title }}**<a class="anchor" href="#{{ slug }}">#</a>
**{% if pdf %}[[pdf]](/papers/{{ pdf }}){% endif %}{% if link %}[[link]]({{ link }}){% endif %}{% if repo %}[[repo]]({{ repo }}){% endif %}[[bibtex]](#{{ slug }}-bibtex){% if award %}<i style="color:red">  {{ award }}</i>{% endif %}**

{% for name in authors %}{{ name }}{{ ", " if not loop.last else "" }}{% endfor %}

{% if conference %}*{{ conference }}*.  {{ location if location else ""}}{{ ", " if location else ""}}{{ month if month else ""}}{{ ", " if month else ""}}{{ year }}.{% else %}{{ location if location else ""}}{{ ", " if location else ""}}{{ month if month else ""}}{{ ", " if month else ""}}{{ year }}.{% endif %}

<div class="bibtex-wrap" id="{{ slug }}-bibtex" hidden>
<pre><code>{{ bibtex|e }}</code></pre>
<button class="bibtex-copy" type="button">copy</button>
</div>

</div>

""")

print("""---
title: "Papers"
date: 2021-06-12T16:51:38-07:00

---

<div class="legend-container">
  <div class="item-container">
      <div class="box pub-conference"></div>
      <span class="label">Conference</span>
  </div>
  <div class="item-container">
      <div class="box pub-journal"></div>
      <span class="label">Journal</span>
  </div>
  <div class="item-container">
      <div class="box pub-workshop"></div>
      <span class="label">Workshop</span>
  </div>
  <div class="item-container">
      <div class="box pub-demoposter"></div>
      <span class="label">Demo or Poster</span>
  </div>
  <div class="item-container">
      <div class="box pub-misc"></div>
      <span class="label">Tech Report</span>
  </div>
  <div class="item-container">
      <div class="box pub-software"></div>
      <span class="label">Software</span>
  </div>
</div>
""")

years = list(cur.execute('SELECT distinct year from papers order by year desc'))
for year_row in years:
    year = year_row['year']
    print(f"""### {year}""")
    for row in cur.execute("SELECT *, month_to_number(month) as month_num FROM papers WHERE year = ? ORDER BY month_num desc;", (year,)):
        try:
            row['slug'] = slugify(row['title'])
            if row.get('year'):
                row['slug'] = f"{row['slug']}-{row['year']}"
            row['bibtex'] = bibtex_for(row)
            row['authors'] = _split_authors(row.pop('authors'))
            print(md_template.render(**row))
        except Exception as e:
            print(len(row), row)
            raise e
#print("""# Conference Publications""")
#for row in cur.execute("SELECT * FROM papers WHERE type = 'conference' ORDER BY year DESC, rowid DESC;"):
#    try:
#        row['authors'] = [x.strip() for x in row.pop('authors').split(',')]
#        print(md_template.render(**row))
#    except Exception as e:
#        print(len(row), row)
#        raise e
#
#print("""# Journal Publications""")
#for row in cur.execute("select * from papers where type = 'journal' order by year desc, rowid DESC;"):
#    try:
#        row['authors'] = [x.strip() for x in row.pop('authors').split(',')]
#        print(md_template.render(**row))
#    except exception as e:
#        print(len(row), row)
#        raise e
#
#print("""# Workshop Publications""")
#for row in cur.execute("select * from papers where type = 'workshop' order by year desc, rowid DESC;"):
#    try:
#        row['authors'] = [x.strip() for x in row.pop('authors').split(',')]
#        print(md_template.render(**row))
#    except exception as e:
#        print(len(row), row)
#        raise e
#
#print("""# Tech Reports, Theses and arXiv""")
#for row in cur.execute("select * from papers where type = 'misc' order by year desc;"):
#    try:
#        row['authors'] = [x.strip() for x in row.pop('authors').split(',')]
#        print(md_template.render(**row))
#    except exception as e:
#        print(len(row), row)
#        raise e
