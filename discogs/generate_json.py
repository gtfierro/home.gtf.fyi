# /// script
# dependencies = [
#     "discogs-client"
# ]
# ///
import discogs_client
import json
import os


def main() -> None:
    token = os.getenv("DISCOGS_USER_TOKEN")
    if not token:
        raise SystemExit("DISCOGS_USER_TOKEN is not set")

    client = discogs_client.Client("my_user_agent/1.0", user_token=token)
    me = client.identity()
    records = []
    for item in me.collection_folders[0].releases:
        names = [artist.name for artist in item.release.artists]
        artist_name = ", ".join(names)
        album_title = item.release.title
        image = item.release.images[0]["uri"] if item.release.images else "No image"
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
