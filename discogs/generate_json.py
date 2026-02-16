# /// script
# dependencies = [
#     "discogs-client"
# ]
# ///
import discogs_client
import json
import os
import time
from typing import Any  # used in type hints


class _Backoff:
    def __init__(self, base_delay: float, max_delay: float) -> None:
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.delay = base_delay

    def next_delay(self) -> float:
        current = self.delay
        self.delay = min(self.delay * 2, self.max_delay)
        return current

    def reset(self) -> None:
        self.delay = self.base_delay



def _iter_collection_with_retry(
    folder: Any,
    backoff: _Backoff,
    *,
    max_attempts: int = 5,
) -> list:
    """Iterate collection pages with retry on rate-limit errors."""
    items = []
    page_num = 1
    while True:
        for attempt in range(1, max_attempts + 1):
            try:
                page = folder.releases.page(page_num)
                break
            except Exception:
                if attempt >= max_attempts:
                    return items
                delay = backoff.next_delay()
                print(f"  Rate limited on page {page_num}, retrying in {delay:.1f}s...")
                time.sleep(delay)
        else:
            break
        backoff.reset()
        if not page:
            break
        items.extend(page)
        page_num += 1
    return items


def main() -> None:
    token = os.getenv("DISCOGS_USER_TOKEN")
    if not token:
        raise SystemExit("DISCOGS_USER_TOKEN is not set")

    client = discogs_client.Client("my_user_agent/1.0", user_token=token)
    me = client.identity()
    records = []
    backoff = _Backoff(base_delay=0.5, max_delay=8.0)
    items = _iter_collection_with_retry(me.collection_folders[0], backoff)
    for item in items:
        # Access release.data directly to avoid triggering lazy API fetches.
        # item.release is pre-populated from basic_information in the
        # collection response, but accessing ListField attrs like .artists
        # can trigger a full /releases/{id} call if the key lookup misses.
        release = item.release
        data = release.data
        artists = data.get("artists", [])
        names = [a["name"] if isinstance(a, dict) else a.name for a in artists]
        artist_name = ", ".join(names)
        album_title = data.get("title", release.title)
        image = data.get("thumb") or data.get("cover_image") or "No image"
        print(f"Found record: {artist_name} - {album_title}")
        records.append(
            {
                "artist": artist_name,
                "title": album_title,
                "image": image,
            }
        )

    with open("records.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
