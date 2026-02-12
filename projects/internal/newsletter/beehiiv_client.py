#!/usr/bin/env python3
"""Beehiiv API client for The Operator's Margin Report newsletter.

Handles subscriber management and post creation via Beehiiv's V2 API.

Usage:
    from beehiiv_client import BeehiivClient

    client = BeehiivClient(api_key="...", publication_id="pub_...")
    client.add_subscriber("operator@dispensary.com", utm_source="glass_website")
    client.list_subscribers(limit=10)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

BASE_URL = "https://api.beehiiv.com/v2"


class BeehiivError(Exception):
    """Raised when the Beehiiv API returns an error."""

    def __init__(self, status: int, message: str, code: str = "UNKNOWN"):
        self.status = status
        self.code = code
        super().__init__(f"[{status}] {code}: {message}")


class BeehiivClient:
    """Client for Beehiiv newsletter API (V2).

    Supports subscriber management and (on eligible plans) post creation.
    """

    def __init__(self, api_key: str, publication_id: str) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        if not publication_id:
            raise ValueError("publication_id is required")
        self.api_key = api_key
        self.publication_id = publication_id
        self._base = f"{BASE_URL}/publications/{publication_id}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Beehiiv API."""
        url = f"{self._base}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url = f"{url}?{query}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = json.dumps(body).encode("utf-8") if body else None
        req = Request(url, data=data, headers=headers, method=method)

        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as e:
            raw_body = e.read().decode("utf-8", errors="replace")
            try:
                err = json.loads(raw_body)
                errors = err.get("errors", [{}])
                msg = errors[0].get("message", raw_body) if errors else raw_body
                code = errors[0].get("code", "API_ERROR") if errors else "API_ERROR"
            except (json.JSONDecodeError, IndexError):
                msg = raw_body
                code = "API_ERROR"
            raise BeehiivError(e.code, msg, code) from e
        except URLError as e:
            raise BeehiivError(0, f"Network error: {e.reason}", "NETWORK_ERROR") from e

    # ------------------------------------------------------------------
    # Subscriber Management
    # ------------------------------------------------------------------

    def add_subscriber(
        self,
        email: str,
        *,
        utm_source: str = "glass_website",
        utm_medium: str = "",
        utm_campaign: str = "",
        referring_site: str = "",
        reactivate_existing: bool = False,
        send_welcome_email: bool = True,
    ) -> dict[str, Any]:
        """Add a new subscriber to the publication.

        Returns the subscriber data dict on success.
        Raises BeehiivError on failure.
        """
        payload: dict[str, Any] = {
            "email": email,
            "reactivate_existing": reactivate_existing,
            "send_welcome_email": send_welcome_email,
        }
        if utm_source:
            payload["utm_source"] = utm_source
        if utm_medium:
            payload["utm_medium"] = utm_medium
        if utm_campaign:
            payload["utm_campaign"] = utm_campaign
        if referring_site:
            payload["referring_site"] = referring_site

        result = self._request("POST", "/subscriptions", body=payload)
        logger.info("Subscriber added: %s (id=%s)", email, result.get("data", {}).get("id"))
        return result.get("data", result)

    def list_subscribers(
        self,
        *,
        limit: int = 10,
        status: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """List subscribers with optional filters.

        Returns dict with 'data' (list), 'has_more', 'next_cursor'.
        """
        params: dict[str, str] = {"limit": str(limit)}
        if status:
            params["status"] = status
        if email:
            params["email"] = email
        return self._request("GET", "/subscriptions", params=params)

    def get_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        """Get a single subscriber by ID."""
        result = self._request("GET", f"/subscriptions/{subscriber_id}")
        return result.get("data", result)

    def delete_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        """Delete (unsubscribe) a subscriber by ID."""
        return self._request("DELETE", f"/subscriptions/{subscriber_id}")

    # ------------------------------------------------------------------
    # Post Management
    # ------------------------------------------------------------------

    def create_post(
        self,
        title: str,
        content_html: str,
        *,
        subtitle: str | None = None,
        status: str = "draft",
    ) -> dict[str, Any]:
        """Create a newsletter post (draft or published).

        NOTE: This endpoint requires the Beehiiv Scale plan or higher.
        On free/lower plans, this will raise BeehiivError with code
        SEND_API_DISABLED. In that case, compose drafts manually in the
        Beehiiv dashboard.

        Args:
            title: Post title.
            content_html: Full HTML content of the newsletter.
            subtitle: Optional subtitle/preview text.
            status: 'draft' (default) or 'confirmed' (publishes immediately).

        Returns:
            Post data dict on success.
        """
        payload: dict[str, Any] = {
            "title": title,
            "status": status,
            "content_html": content_html,
        }
        if subtitle:
            payload["subtitle"] = subtitle

        try:
            result = self._request("POST", "/posts", body=payload)
            logger.info("Post created: %s (status=%s)", title, status)
            return result.get("data", result)
        except BeehiivError as e:
            if e.code == "SEND_API_DISABLED":
                logger.warning(
                    "Post creation API is disabled on this Beehiiv plan. "
                    "Draft the newsletter manually in the Beehiiv dashboard. "
                    "Original error: %s",
                    e,
                )
            raise

    def list_posts(self, *, limit: int = 10, status: str | None = None) -> dict[str, Any]:
        """List posts with optional status filter."""
        params: dict[str, str] = {"limit": str(limit)}
        if status:
            params["status"] = status
        return self._request("GET", "/posts", params=params)

    # ------------------------------------------------------------------
    # Publication Stats
    # ------------------------------------------------------------------

    def get_publication(self) -> dict[str, Any]:
        """Get publication details."""
        result = self._request("GET", "")
        return result.get("data", result)

    def get_stats(self) -> dict[str, Any]:
        """Get publication stats summary.

        Returns subscriber count, publication info, and plan capabilities.
        """
        pub = self.get_publication()
        subs = self.list_subscribers(limit=1)

        # Probe post creation capability via list_posts
        # On free plans, the posts endpoint itself returns 403/SEND_API_DISABLED
        can_create_posts = True
        try:
            self.list_posts(limit=1)
        except BeehiivError as e:
            if e.code == "SEND_API_DISABLED" or e.status == 403:
                can_create_posts = False

        # Count active subscribers
        active_subs = self.list_subscribers(limit=100, status="active")
        active_count = len(active_subs.get("data", []))
        has_more = active_subs.get("has_more", False)

        return {
            "publication": pub,
            "subscriber_count": active_count,
            "subscriber_count_has_more": has_more,
            "can_create_posts": can_create_posts,
        }


# ------------------------------------------------------------------
# CLI for testing
# ------------------------------------------------------------------

def _cli() -> None:
    """Simple CLI for testing the client."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Beehiiv API client CLI")
    parser.add_argument("action", choices=["stats", "subscribers", "add", "test-post"])
    parser.add_argument("--email", help="Email for add action")
    parser.add_argument("--api-key", default=os.environ.get("BEEHIIV_API_KEY"))
    parser.add_argument(
        "--pub-id",
        default=os.environ.get("BEEHIIV_PUBLICATION_ID"),
    )
    args = parser.parse_args()

    if not args.api_key or not args.pub_id:
        print("Error: Set BEEHIIV_API_KEY and BEEHIIV_PUBLICATION_ID env vars or use --api-key/--pub-id")
        raise SystemExit(1)

    client = BeehiivClient(args.api_key, args.pub_id)

    if args.action == "stats":
        stats = client.get_stats()
        print(json.dumps(stats, indent=2, default=str))

    elif args.action == "subscribers":
        subs = client.list_subscribers(limit=50)
        print(json.dumps(subs, indent=2, default=str))

    elif args.action == "add":
        if not args.email:
            print("Error: --email required for add action")
            raise SystemExit(1)
        result = client.add_subscriber(args.email)
        print(json.dumps(result, indent=2, default=str))

    elif args.action == "test-post":
        try:
            result = client.create_post(
                title="Test Post from Pipeline",
                content_html="<p>This is a test post from the newsletter pipeline.</p>",
                status="draft",
            )
            print(json.dumps(result, indent=2, default=str))
        except BeehiivError as e:
            print(f"Post creation failed: {e}")
            if e.code == "SEND_API_DISABLED":
                print("→ Post creation requires the Scale plan. Use Beehiiv dashboard to create posts manually.")


if __name__ == "__main__":
    _cli()
