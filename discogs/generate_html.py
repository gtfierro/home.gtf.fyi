# /// script
# dependencies = [
#     "jinja2"
# ]
# ///
import json
from jinja2 import Environment, select_autoescape


TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Random Record</title>
    <style>
      :root {
        --bg: #f6f0e8;
        --fg: #161616;
        --card: rgba(255, 255, 255, 0.84);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Georgia", "Times New Roman", serif;
        color: var(--fg);
        background:
          radial-gradient(circle at 20% 20%, #ffe9c6, transparent 45%),
          radial-gradient(circle at 80% 10%, #d7ecff, transparent 40%),
          radial-gradient(circle at 70% 80%, #ffd6de, transparent 45%),
          var(--bg);
      }
      #card {
        display: flex;
        gap: 3rem;
        align-items: center;
        padding: 4rem 5rem;
        border-radius: 24px;
        background: var(--card);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
        max-width: 1200px;
        width: min(96vw, 1200px);
      }
      #cover {
        width: min(45vw, 520px);
        max-height: 70vh;
        object-fit: cover;
        border-radius: 18px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
      }
      #title {
        margin: 0;
        font-size: clamp(0.7rem, 1.75vw, 1.625rem);
        line-height: 0.95;
        letter-spacing: 0.01em;
      }
      #artist {
        margin: 1.5rem 0 0;
        font-size: clamp(0.6rem, 1.5vw, 1.375rem);
        line-height: 1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      @media (max-width: 900px) {
        #card {
          flex-direction: column;
          padding: 3rem 2rem;
          text-align: center;
        }
        #cover {
          width: min(80vw, 420px);
        }
      }
    </style>
  </head>
  <body>
    <main id="card" aria-live="polite">
      <img id="cover" alt="">
      <div>
        <h1 id="title"></h1>
        <h2 id="artist"></h2>
      </div>
    </main>

    <script id="records-data" type="application/json">{{ records_json | safe }}</script>
    <script>
      const records = JSON.parse(document.getElementById('records-data').textContent);
      const title = document.getElementById('title');
      const artist = document.getElementById('artist');
      const cover = document.getElementById('cover');

      const pickRandom = () => {
        if (!records.length) {
          title.textContent = 'No records found';
          artist.textContent = '';
          cover.style.display = 'none';
          return;
        }
        const record = records[Math.floor(Math.random() * records.length)];
        title.textContent = record.title;
        artist.textContent = record.artist;
        if (record.image && record.image !== 'No image') {
          cover.src = record.image;
          cover.alt = `${record.title} cover`;
          cover.style.display = '';
        } else {
          cover.removeAttribute('src');
          cover.alt = 'No cover image available';
          cover.style.display = 'none';
        }
      };

      window.addEventListener('DOMContentLoaded', pickRandom);
    </script>
  </body>
</html>
"""


def main() -> None:
    with open("records.json", "r", encoding="utf-8") as f:
        records = json.load(f)

    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    records_json = json.dumps(records, ensure_ascii=False)
    html = env.from_string(TEMPLATE).render(records_json=records_json)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
