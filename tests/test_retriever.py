from src.agent.retriever import KnowledgeBase


def test_retriever_returns_results():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search("What is the return window?", top_k=3)

    assert results
    assert len(results) <= 3


def test_retriever_returns_relevant_return_content():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search("How many days do I have to return an item?", top_k=3)

    combined_text = " ".join(
        result.document.content.lower()
        for result in results
    )

    assert "return" in combined_text


def test_results_contain_source_metadata():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search("international shipping", top_k=3)

    for result in results:
        assert result.document.filename
        assert result.document.heading
        assert result.score >= -1
        assert result.score <= 1

from src.agent.sources import format_source


def test_current_policy_is_preferred_over_legacy():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search(
        "What is the return period for an item?",
        top_k=5,
    )

    filenames = [
        result.document.filename
        for result in results
    ]

    current_index = next(
        (
            i
            for i, filename in enumerate(filenames)
            if "current" in filename.lower()
        ),
        None,
    )

    legacy_index = next(
        (
            i
            for i, filename in enumerate(filenames)
            if "legacy" in filename.lower()
        ),
        None,
    )

    if current_index is not None and legacy_index is not None:
        assert current_index < legacy_index


def test_source_contains_filename_and_heading():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search(
        "international shipping",
        top_k=1,
    )

    source = format_source(results[0])

    assert results[0].document.filename in source
    assert results[0].document.heading in source


def test_search_keeps_original_document_content():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search(
        "return policy",
        top_k=3,
    )

    for result in results:
        assert result.document.content
        assert result.document.filename