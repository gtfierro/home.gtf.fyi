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
    <title>Records by Genre</title>
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
        font-family: "Georgia", "Times New Roman", serif;
        color: var(--fg);
        background:
          radial-gradient(circle at 20% 20%, #ffe9c6, transparent 45%),
          radial-gradient(circle at 80% 10%, #d7ecff, transparent 40%),
          radial-gradient(circle at 70% 80%, #ffd6de, transparent 45%),
          var(--bg);
        padding: 2.5rem clamp(1rem, 4vw, 4rem);
      }
      header {
        max-width: 1200px;
        margin: 0 auto 2rem;
        text-align: center;
      }
      h1 {
        margin: 0 0 1.5rem;
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        letter-spacing: 0.02em;
      }
      .controls {
        display: flex;
        gap: 0.75rem;
        justify-content: center;
        flex-wrap: wrap;
      }
      #genre-input {
        font-family: inherit;
        font-size: 1rem;
        padding: 0.6rem 1rem;
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        background: var(--card);
        color: var(--fg);
        width: min(70vw, 360px);
      }
      #count {
        margin: 1rem 0 0;
        font-size: 0.95rem;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      #grid {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1.25rem;
      }
      .album {
        background: var(--card);
        border-radius: 14px;
        padding: 0.75rem;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        text-align: center;
      }
      .album img {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 10px;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.2);
      }
      .album .title {
        margin: 0.6rem 0 0;
        font-size: 0.85rem;
        line-height: 1.15;
      }
      .album .artist {
        margin: 0.3rem 0 0;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.7;
      }
      .album .genres {
        margin: 0.45rem 0 0;
        font-size: 0.62rem;
        font-style: italic;
        line-height: 1.25;
        opacity: 0.55;
      }
      .album.highlight {
        outline: 3px solid #d2691e;
        outline-offset: 2px;
        box-shadow: 0 0 0 6px rgba(210, 105, 30, 0.25), 0 16px 36px rgba(0, 0, 0, 0.25);
        animation: pulse 0.6s ease-out;
      }
      @keyframes pulse {
        0% { transform: scale(1); }
        45% { transform: scale(1.06); }
        100% { transform: scale(1); }
      }
      #random-btn {
        font-family: inherit;
        font-size: 1rem;
        padding: 0.6rem 1.4rem;
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        background: var(--fg);
        color: var(--bg);
        cursor: pointer;
      }
      #random-btn:hover { opacity: 0.85; }
      #empty {
        max-width: 1200px;
        margin: 3rem auto;
        text-align: center;
        font-size: 1.1rem;
        opacity: 0.6;
      }
    </style>
  </head>
  <body>
    <header>
      <h1>Records by Genre</h1>
      <div class="controls">
        <input
          id="genre-input"
          type="text"
          placeholder='Type a genre, or "all genre"'
          value="all genre"
          autocomplete="off"
          aria-label="Filter by genre">
        <button id="random-btn" type="button">Random</button>
      </div>
      <p id="count"></p>
    </header>

    <main id="grid" aria-live="polite"></main>
    <p id="empty" hidden>No records match that genre.</p>

    <script id="records-data" type="application/json">{{ records_json | safe }}</script>
    <script>
      const records = JSON.parse(document.getElementById('records-data').textContent);
      const input = document.getElementById('genre-input');
      const grid = document.getElementById('grid');
      const empty = document.getElementById('empty');
      const count = document.getElementById('count');
      const randomBtn = document.getElementById('random-btn');
      let cards = [];

      const imageUrlFor = (record) =>
        (record.image_high_res && record.image_high_res !== 'No image' && record.image_high_res) ||
        (record.image && record.image !== 'No image' && record.image) ||
        null;

      const matches = (record, query) => {
        const q = query.trim().toLowerCase();
        if (q === '' || q === 'all genre' || q === 'all genres') return true;
        return (record.genres || []).some((g) => String(g).toLowerCase().includes(q));
      };

      const render = () => {
        const query = input.value;
        const filtered = records.filter((r) => matches(r, query));
        grid.innerHTML = '';
        cards = [];
        empty.hidden = filtered.length !== 0;
        randomBtn.disabled = filtered.length === 0;
        count.textContent = filtered.length
          ? `${filtered.length} record${filtered.length === 1 ? '' : 's'}`
          : '';

        for (const record of filtered) {
          const card = document.createElement('div');
          card.className = 'album';

          const url = imageUrlFor(record);
          if (url) {
            const img = document.createElement('img');
            img.src = url;
            img.alt = `${record.title} cover`;
            img.loading = 'lazy';
            card.appendChild(img);
          }

          const title = document.createElement('p');
          title.className = 'title';
          title.textContent = record.title;
          card.appendChild(title);

          const artist = document.createElement('p');
          artist.className = 'artist';
          artist.textContent = record.artist;
          card.appendChild(artist);

          const genreList = record.genres || [];
          if (genreList.length) {
            const genres = document.createElement('p');
            genres.className = 'genres';
            genres.textContent = genreList.join(' · ');
            card.appendChild(genres);
          }

          grid.appendChild(card);
          cards.push(card);
        }
      };

      const pickRandom = () => {
        if (!cards.length) return;
        const previous = grid.querySelector('.album.highlight');
        if (previous) previous.classList.remove('highlight');
        const card = cards[Math.floor(Math.random() * cards.length)];
        // Re-trigger the pulse animation even if the same card is picked.
        void card.offsetWidth;
        card.classList.add('highlight');
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      };

      input.addEventListener('input', render);
      randomBtn.addEventListener('click', pickRandom);
      window.addEventListener('DOMContentLoaded', render);
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
    with open("genre.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
