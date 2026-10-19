from .base import Provider, Offer, RouteResult

def get(name: str, **kw) -> Provider:
    name = (name or "").lower()
    if name == "amadeus":
        from .amadeus import AmadeusProvider
        return AmadeusProvider(**kw)
    if name == "serpapi":
        from .serpapi import SerpApiProvider
        return SerpApiProvider(**kw)
    if name == "mock":
        from .mock import MockProvider
        return MockProvider(**kw)
    raise SystemExit(f"unknown provider {name!r}. use: amadeus, serpapi, mock")
