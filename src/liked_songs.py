# src/liked_songs.py

from typing import List, Dict, Any, Optional
from datetime import datetime

from spotipy import Spotify


def fetch_all_liked_tracks(
    sp: Spotify,
    limit: int = 50,
    max_tracks: Optional[int] = None,
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    """
    Fetch all 'Liked Songs' (saved tracks) for the current user.

    Returns the raw items Spotify gives you (each has 'added_at' and 'track').
    """
    items: List[Dict[str, Any]] = []

    results = sp.current_user_saved_tracks(limit=limit)
    batch = results.get("items", [])
    items.extend(batch)

    if verbose:
        print(f"Fetched {len(items)} tracks so far...")

    while results.get("next"):
        if max_tracks is not None and len(items) >= max_tracks:
            if verbose:
                print(f"Reached max_tracks={max_tracks}, stopping.")
            break

        results = sp.next(results)
        batch = results.get("items", [])
        items.extend(batch)

        if verbose:
            print(f"Fetched {len(items)} tracks so far...")

        if max_tracks is not None and len(items) >= max_tracks:
            if verbose:
                print(f"Reached max_tracks={max_tracks}, stopping.")
            break

    return items[:max_tracks] if max_tracks is not None else items


def flatten_liked_tracks(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Turn the raw saved-track items into a flat list of dicts for DataFrame use.
    """
    flat: List[Dict[str, Any]] = []

    for entry in items:
        added_at = entry.get("added_at")
        track = entry.get("track") or {}
        album = track.get("album") or {}
        artists = track.get("artists") or []

        artist_names = [a.get("name") for a in artists if a.get("name")]
        artist_ids = [a.get("id") for a in artists if a.get("id")]

        # Parse 'added_at' (ISO 8601 with Z)
        added_dt = None
        if added_at:
            try:
                added_dt = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
            except Exception:
                added_dt = None

        # Parse album release date (often YYYY-MM-DD / YYYY-MM / YYYY)
        album_release_date = album.get("release_date")
        album_release_dt = None
        if album_release_date:
            for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
                try:
                    album_release_dt = datetime.strptime(album_release_date, fmt)
                    break
                except Exception:
                    continue

        flat.append(
            {
                "added_at": added_at,
                "added_at_datetime": added_dt,

                "track_id": track.get("id"),
                "track_name": track.get("name"),
                "track_popularity": track.get("popularity"),
                "explicit": track.get("explicit"),
                "duration_ms": track.get("duration_ms"),
                "duration_min": (track.get("duration_ms") or 0) / 60000.0,
                "track_number": track.get("track_number"),
                "disc_number": track.get("disc_number"),

                "album_id": album.get("id"),
                "album_name": album.get("name"),
                "album_release_date": album_release_date,
                "album_release_datetime": album_release_dt,
                "album_total_tracks": album.get("total_tracks"),

                "artist_names": artist_names,
                "artist_ids": artist_ids,
                "primary_artist_name": artist_names[0] if artist_names else None,
                "primary_artist_id": artist_ids[0] if artist_ids else None,

                "is_local": track.get("is_local"),
                "preview_url": track.get("preview_url"),
                "spotify_url": (track.get("external_urls") or {}).get("spotify"),
                "uri": track.get("uri"),
            }
        )

    return flat
