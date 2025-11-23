# src/spotify_auth.py

import os
from typing import Optional

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_spotify_client(scopes: Optional[str] = None) -> spotipy.Spotify:
    """
    Return an authenticated Spotipy client.

    Reads SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
    from a .env file in the project root (via python-dotenv) or from
    the environment.

    The redirect URI must match EXACTLY one of the redirect URIs
    configured in your Spotify developer app.
    """
    # Load .env from current working dir / project root
    load_dotenv()

    cid = os.getenv("SPOTIPY_CLIENT_ID")
    sec = os.getenv("SPOTIPY_CLIENT_SECRET")
    redir = os.getenv("SPOTIPY_REDIRECT_URI")

    if not cid or not sec or not redir:
        missing = []
        if not cid:
            missing.append("SPOTIPY_CLIENT_ID")
        if not sec:
            missing.append("SPOTIPY_CLIENT_SECRET")
        if not redir:
            missing.append("SPOTIPY_REDIRECT_URI")
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    if scopes is None:
        scopes = "user-library-read"

    auth = SpotifyOAuth(
        client_id=cid,
        client_secret=sec,
        redirect_uri=redir,
        scope=scopes,
        cache_path=".spotipyoauthcache",  # token cache file
        show_dialog=False,
    )

    sp = spotipy.Spotify(auth_manager=auth)
    return sp
