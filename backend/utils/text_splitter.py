"""
Text Splitting Utilities

Intelligent text splitting for markdown documents with section-aware chunking.
"""

import re
from dataclasses import dataclass


@dataclass
class MarkdownChunk:
    """Represents a chunk of markdown text with metadata."""

    content: str
    section_title: str
    section_level: int
    chunk_index: int
    total_chunks: int


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses simple heuristic: ~4 characters per token (conservative estimate).

    Args:
        text: Input text

    Returns:
        Estimated token count

    Example:
        >>> estimate_tokens("Hello world")
        3
    """
    # Conservative estimate: 4 chars per token
    # This is safer than the standard ~3.5 chars/token
    return len(text) // 4


def split_markdown_by_sections(
    markdown_text: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[MarkdownChunk]:
    """
    Split markdown text by sections (H2/H3) with intelligent chunking.

    Strategy:
    1. Split by H2 (##) and H3 (###) headers
    2. If section is too large, chunk it with overlap
    3. Preserve section context in metadata

    Args:
        markdown_text: Markdown content to split
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Token overlap between chunks

    Returns:
        List of MarkdownChunk objects with content and metadata

    Example:
        >>> text = "## Section 1\\nContent here\\n## Section 2\\nMore content"
        >>> chunks = split_markdown_by_sections(text, max_tokens=100)
        >>> len(chunks)
        2
    """
    # Pattern to match H2 (##) and H3 (###) headers
    # Captures: (header_level, title, content)
    section_pattern = r"^(#{2,3})\s+(.+?)$"

    lines = markdown_text.split("\n")
    sections = []
    current_section = None
    current_content = []

    for line in lines:
        match = re.match(section_pattern, line)
        if match:
            # Save previous section
            if current_section:
                sections.append(
                    {
                        "level": current_section["level"],
                        "title": current_section["title"],
                        "content": "\n".join(current_content).strip(),
                    }
                )
                current_content = []

            # Start new section
            header_level = len(match.group(1))  # Count # characters
            title = match.group(2).strip()
            current_section = {"level": header_level, "title": title}
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        sections.append(
            {
                "level": current_section["level"],
                "title": current_section["title"],
                "content": "\n".join(current_content).strip(),
            }
        )

    # Convert sections to chunks
    all_chunks = []

    for section in sections:
        section_chunks = _chunk_section(
            section["content"],
            section["title"],
            section["level"],
            max_tokens,
            overlap_tokens,
        )
        all_chunks.extend(section_chunks)

    return all_chunks


def _chunk_section(
    content: str,
    section_title: str,
    section_level: int,
    max_tokens: int,
    overlap_tokens: int,
) -> list[MarkdownChunk]:
    """
    Split a single section into chunks if needed.

    Args:
        content: Section content
        section_title: Section title
        section_level: Header level (2 or 3)
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Token overlap

    Returns:
        List of MarkdownChunk objects
    """
    if not content.strip():
        return []

    # Estimate tokens for entire section
    total_tokens = estimate_tokens(content)

    # If section fits in one chunk, return it
    if total_tokens <= max_tokens:
        return [
            MarkdownChunk(
                content=content,
                section_title=section_title,
                section_level=section_level,
                chunk_index=0,
                total_chunks=1,
            )
        ]

    # Split into chunks with overlap
    chunks = []
    lines = content.split("\n")
    current_chunk = []
    current_tokens = 0

    for line in lines:
        line_tokens = estimate_tokens(line)

        # If adding this line exceeds limit, save current chunk
        if current_tokens + line_tokens > max_tokens and current_chunk:
            chunk_content = "\n".join(current_chunk)
            chunks.append(chunk_content)

            # Keep overlap for next chunk
            overlap_lines = []
            overlap_tok_count = 0
            for prev_line in reversed(current_chunk):
                prev_tokens = estimate_tokens(prev_line)
                if overlap_tok_count + prev_tokens <= overlap_tokens:
                    overlap_lines.insert(0, prev_line)
                    overlap_tok_count += prev_tokens
                else:
                    break

            current_chunk = overlap_lines
            current_tokens = overlap_tok_count

        current_chunk.append(line)
        current_tokens += line_tokens

    # Add final chunk
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    # Convert to MarkdownChunk objects
    total_chunks = len(chunks)
    return [
        MarkdownChunk(
            content=chunk,
            section_title=section_title,
            section_level=section_level,
            chunk_index=idx,
            total_chunks=total_chunks,
        )
        for idx, chunk in enumerate(chunks)
    ]
