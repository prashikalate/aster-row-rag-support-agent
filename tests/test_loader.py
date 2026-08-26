from src.agent.loader import load_documents


def test_knowledge_base_loads():
    documents = load_documents("knowledge-base")

    assert documents
    assert len(documents) > 0


def test_documents_keep_source_metadata():
    documents = load_documents("knowledge-base")

    first = documents[0]

    assert first.filename
    assert first.title
    assert first.heading
    assert first.content


def test_documents_are_split_by_heading():
    documents = load_documents("knowledge-base")

    headings = {document.heading for document in documents}

    assert len(headings) > 1