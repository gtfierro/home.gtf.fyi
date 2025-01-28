# /// script
# requires-python = "==3.11"
# dependencies = [
#   "jinja2",
# ]
# ///
import sys
import jinja2
import sqlite3

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

con = sqlite3.connect('papers.db')
con.row_factory = dict_factory
con.create_function('month_to_number', 1, month_to_number)
cur = con.cursor()

md_template = jinja2.Template("""
<div class="pub pub-{{ type }}">

**{{ title }}**
**{% if pdf %}[[pdf]](/papers/{{ pdf }}){% endif %}{% if link %}[[link]]({{ link }}){% endif %}{% if award %}<i style="color:red">  {{ award }}</i>{% endif %}**

{% for name in authors %}{{ name }}{{ ", " if not loop.last else "" }}{% endfor %}

*{{ conference if conference else ""}}*{{ ". " if conference else ""}} {{ location if location else ""}}{{ ", " if location else ""}}{{ month if month else ""}}{{ ", " if month else ""}}{{ year }}.

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
</div>
""")

years = list(cur.execute('SELECT distinct year from papers order by year desc'))
for year_row in years:
    year = year_row['year']
    print(f"""### {year}""")
    for row in cur.execute("SELECT *, month_to_number(month) as month_num FROM papers WHERE year = ? ORDER BY month_num desc;", (year,)):
        try:
            row['authors'] = [x.strip() for x in row.pop('authors').split(',')]
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
