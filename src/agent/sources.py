def format_source(result) -> str:
    """Format one retrieval result as a customer-facing source reference."""

    return f"{result.document.filename} — {result.document.heading}"


def format_sources(results) -> list[str]:
    """Return unique human-readable source references."""

    sources = []

    for result in results:
        source = format_source(result)

        if source not in sources:
            sources.append(source)

    return sources