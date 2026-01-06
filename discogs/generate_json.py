# /// script
# dependencies = [
#     "discogs-client"
# ]
# ///
import discogs_client
import json
import os
import time
from typing import Any, Sequence


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


def _get_release_images_with_retry(
    release: Any,
    backoff: _Backoff,
    *,
    max_attempts: int = 5,
) -> Sequence[dict]:
    for attempt in range(1, max_attempts + 1):
        try:
            images = release.images
        except Exception:
            if attempt >= max_attempts:
                return []
            time.sleep(backoff.next_delay())
            try:
                if hasattr(release, "refresh"):
                    release.refresh()
                elif hasattr(release, "fetch"):
                    release.fetch()
            except Exception:
                pass
        else:
            backoff.reset()
            return images
    return []


def main() -> None:
    token = os.getenv("DISCOGS_USER_TOKEN")
    if not token:
        raise SystemExit("DISCOGS_USER_TOKEN is not set")

    client = discogs_client.Client("my_user_agent/1.0", user_token=token)
    me = client.identity()
    records = []
    backoff = _Backoff(base_delay=0.5, max_delay=8.0)
    for item in me.collection_folders[0].releases:
        names = [artist.name for artist in item.release.artists]
        artist_name = ", ".join(names)
        album_title = item.release.title
        images = _get_release_images_with_retry(item.release, backoff)
        image = images[0]["uri"] if images else "No image"
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
