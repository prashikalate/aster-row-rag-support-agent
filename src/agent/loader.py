from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class Document:
    filename: str
    title: str
    status: str
    document_type: str
    priority: int
    heading: str
    content: str


def parse_front_matter(text: str) -> tuple[dict, str]:
    """
    Parse simple YAML-style front matter from a Markdown document.
    """

    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) != 3:
        return {}, text

    raw_metadata = parts[1].strip()
    content = parts[2].strip()

    metadata = {}

    for line in raw_metadata.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")

    return metadata, content


def split_by_headings(content: str) -> list[tuple[str, str]]:
    """
    Split Markdown content into sections based on headings.
    """

    pattern = r"(?m)^(#{1,6})\s+(.+?)\s*$"
    matches = list(re.finditer(pattern, content))

    if not matches:
        return [("Document", content.strip())]

    sections = []

    for index, match in enumerate(matches):
        heading = match.group(2).strip()

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)

        section_content = content[start:end].strip()

        if section_content:
            sections.append((heading, section_content))

    return sections


def load_documents(knowledge_base_path: str) -> list[Document]:
    """
    Load all Markdown documents from the knowledge base.

    Each heading becomes a separately retrievable document chunk.
    """

    base_path = Path(knowledge_base_path)

    documents = []

    for file_path in sorted(base_path.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")

        metadata, content = parse_front_matter(text)

        title = metadata.get("title", file_path.stem)
        status = metadata.get("status", "unknown")
        document_type = metadata.get("type", "unknown")

        try:
            priority = int(metadata.get("priority", 0))
        except ValueError:
            priority = 0

        sections = split_by_headings(content)

        for heading, section_content in sections:
            documents.append(
                Document(
                    filename=file_path.name,
                    title=title,
                    status=status,
                    document_type=document_type,
                    priority=priority,
                    heading=heading,
                    content=section_content,
                )
            )

    return documents