"""Cohesion and coherence metrics.

This module measures how well a text holds together structurally (cohesion)
and semantically (coherence). Important for analyzing writing quality and
authorial sophistication.

Related GitHub Issue:
    #22 - Cohesion and Coherence Metrics
    https://github.com/craigtrim/pystylometry/issues/22

References:
    Halliday, M. A. K., & Hasan, R. (1976). Cohesion in English. Longman.
    Graesser, A. C., McNamara, D. S., & Kulikowich, J. M. (2011). Coh-Metrix:
        Providing multilevel analyses of text characteristics. Educational
        Researcher, 40(5), 223-234.
    McNamara, D. S., et al. (2010). Automated evaluation of text and discourse
        with Coh-Metrix. Cambridge University Press.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .._types import CohesionCoherenceResult
from .._utils import check_optional_dependency

# ========== Connective Word Lists ==========
# Categorized based on Halliday & Hasan (1976) and Coh-Metrix documentation

ADDITIVE_CONNECTIVES: set[str] = {
    # Addition
    "and",
    "also",
    "furthermore",
    "moreover",
    "additionally",
    "besides",
    "likewise",
    "similarly",
    "equally",
    "too",
    "as well",
    "in addition",
    "what is more",
    "not only",
    "along with",
}

ADVERSATIVE_CONNECTIVES: set[str] = {
    # Contrast/opposition
    "but",
    "however",
    "nevertheless",
    "nonetheless",
    "yet",
    "although",
    "though",
    "whereas",
    "while",
    "despite",
    "in spite of",
    "on the other hand",
    "conversely",
    "instead",
    "rather",
    "still",
    "even so",
    "on the contrary",
    "by contrast",
    "notwithstanding",
}

CAUSAL_CONNECTIVES: set[str] = {
    # Cause and effect
    "because",
    "therefore",
    "thus",
    "hence",
    "consequently",
    "accordingly",
    "so",
    "since",
    "as a result",
    "for this reason",
    "due to",
    "owing to",
    "thereby",
    "wherefore",
    "for",
    "as",
    "given that",
    "in order to",
    "so that",
}

TEMPORAL_CONNECTIVES: set[str] = {
    # Time/sequence
    "then",
    "after",
    "before",
    "when",
    "while",
    "during",
    "afterwards",
    "meanwhile",
    "subsequently",
    "previously",
    "first",
    "second",
    "third",
    "finally",
    "next",
    "later",
    "earlier",
    "soon",
    "immediately",
    "eventually",
    "at last",
    "in the end",
    "at first",
    "at the same time",
    "once",
    "until",
    "since",
}

# All connectives combined for lookup
ALL_CONNECTIVES: set[str] = (
    ADDITIVE_CONNECTIVES | ADVERSATIVE_CONNECTIVES | CAUSAL_CONNECTIVES | TEMPORAL_CONNECTIVES
)

# Demonstrative pronouns/determiners (for referential cohesion)
DEMONSTRATIVES: set[str] = {"this", "that", "these", "those"}

# Content word POS tags (for lexical cohesion)
CONTENT_POS_TAGS: set[str] = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}

# Pronoun POS tags
PRONOUN_POS_TAGS: set[str] = {"PRON"}


def _count_words(text: str) -> int:
    """Count words in text using simple tokenization."""
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return len(words)


def _tokenize_simple(text: str) -> list[str]:
    """Simple word tokenization."""
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using simple heuristics."""
    # Split on sentence-ending punctuation followed by space or end of string
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs based on blank lines."""
    # Split on double newlines or multiple newlines
    paragraphs = re.split(r"\n\s*\n", text.strip())
    # Filter out empty paragraphs
    return [p.strip() for p in paragraphs if p.strip()]


def _jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0  # Both empty sets are identical
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def _count_connectives(tokens: list[str]) -> dict[str, int]:
    """Count connectives by category from tokenized text."""
    text_lower = " ".join(tokens)

    counts = {
        "additive": 0,
        "adversative": 0,
        "causal": 0,
        "temporal": 0,
    }

    # Check multi-word connectives first (in the joined text)
    multi_word_connectives = [c for c in ALL_CONNECTIVES if " " in c]
    for connective in multi_word_connectives:
        occurrences = text_lower.count(connective)
        if occurrences > 0:
            if connective in ADDITIVE_CONNECTIVES:
                counts["additive"] += occurrences
            elif connective in ADVERSATIVE_CONNECTIVES:
                counts["adversative"] += occurrences
            elif connective in CAUSAL_CONNECTIVES:
                counts["causal"] += occurrences
            elif connective in TEMPORAL_CONNECTIVES:
                counts["temporal"] += occurrences

    # Check single-word connectives
    single_word_connectives = [c for c in ALL_CONNECTIVES if " " not in c]
    for token in tokens:
        if token in single_word_connectives:
            if token in ADDITIVE_CONNECTIVES:
                counts["additive"] += 1
            elif token in ADVERSATIVE_CONNECTIVES:
                counts["adversative"] += 1
            elif token in CAUSAL_CONNECTIVES:
                counts["causal"] += 1
            elif token in TEMPORAL_CONNECTIVES:
                counts["temporal"] += 1

    return counts


def _get_content_words_from_doc(doc: Any) -> list[str]:
    """Extract lemmatized content words from a spaCy doc."""
    return [
        token.lemma_.lower() for token in doc if token.pos_ in CONTENT_POS_TAGS and token.is_alpha
    ]


def _compute_word_repetition(sentences: list[list[str]]) -> float:
    """Compute word repetition ratio across sentences.

    Measures how many content words appear in multiple sentences.
    """
    if len(sentences) < 2:
        return 0.0

    # Flatten all words
    all_words = [w for sent in sentences for w in sent]
    if not all_words:
        return 0.0

    # Count words appearing in more than one sentence
    word_to_sentences: dict[str, set[int]] = {}
    for i, sent in enumerate(sentences):
        for word in sent:
            if word not in word_to_sentences:
                word_to_sentences[word] = set()
            word_to_sentences[word].add(i)

    repeated_words = sum(1 for word, sents in word_to_sentences.items() if len(sents) > 1)
    unique_words = len(word_to_sentences)

    return repeated_words / unique_words if unique_words > 0 else 0.0


def _compute_lexical_chains(
    sentences: list[list[str]], min_chain_length: int = 2
) -> list[list[str]]:
    """Compute simplified lexical chains based on word repetition.

    A lexical chain is a sequence of related words spanning multiple sentences.
    This simplified version uses exact word matches (lemmatized).

    Args:
        sentences: List of sentences, each as list of content words
        min_chain_length: Minimum occurrences to form a chain

    Returns:
        List of lexical chains (each chain is a list of word occurrences)
    """
    if len(sentences) < 2:
        return []

    # Track word appearances across sentences
    word_positions: dict[str, list[tuple[int, str]]] = {}
    for sent_idx, sent in enumerate(sentences):
        for word in sent:
            if word not in word_positions:
                word_positions[word] = []
            word_positions[word].append((sent_idx, word))

    # Words appearing in multiple sentences form chains
    chains = []
    for word, positions in word_positions.items():
        # Get unique sentences this word appears in
        unique_sentences = set(pos[0] for pos in positions)
        if len(unique_sentences) >= min_chain_length:
            chains.append([word] * len(positions))

    return chains


def _compute_anaphora_metrics(doc: Any) -> tuple[int, float]:
    """Compute anaphora count and resolution ratio.

    Uses heuristics to detect anaphoric references (pronouns with potential antecedents).

    Returns:
        Tuple of (anaphora_count, resolution_ratio)
    """
    pronouns = []
    nouns = []

    for token in doc:
        if token.pos_ == "PRON" and token.is_alpha:
            pronouns.append(token)
        elif token.pos_ in ("NOUN", "PROPN") and token.is_alpha:
            nouns.append(token)

    anaphora_count = len(pronouns)

    if anaphora_count == 0:
        return 0, 1.0  # No pronouns, perfect resolution (vacuously true)

    # Heuristic: pronouns that have a noun before them are "resolvable"
    # This is a simplification - true anaphora resolution requires coreference
    resolved = 0
    for pron in pronouns:
        # Check if there's a noun before this pronoun in the text
        if any(noun.i < pron.i for noun in nouns):
            resolved += 1

    resolution_ratio = resolved / anaphora_count if anaphora_count > 0 else 1.0
    return anaphora_count, resolution_ratio


def _compute_adjacent_overlap(sentences: list[list[str]]) -> float:
    """Compute mean content word overlap between adjacent sentences."""
    if len(sentences) < 2:
        return 0.0

    overlaps = []
    for i in range(len(sentences) - 1):
        set1 = set(sentences[i])
        set2 = set(sentences[i + 1])
        overlaps.append(_jaccard_similarity(set1, set2))

    return sum(overlaps) / len(overlaps) if overlaps else 0.0


def _compute_mean_sentence_similarity(sentences: list[list[str]]) -> float:
    """Compute mean pairwise similarity between all sentences."""
    if len(sentences) < 2:
        return 1.0  # Single sentence is perfectly coherent with itself

    similarities = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            set1 = set(sentences[i])
            set2 = set(sentences[j])
            similarities.append(_jaccard_similarity(set1, set2))

    return sum(similarities) / len(similarities) if similarities else 0.0


def _compute_paragraph_topic_consistency(paragraphs: list[list[str]]) -> float:
    """Compute topic consistency within paragraphs.

    Measures how consistent the vocabulary is within each paragraph.
    """
    if not paragraphs:
        return 0.0

    consistencies = []
    for para_words in paragraphs:
        if len(para_words) < 2:
            continue
        # Consistency = repetition rate within paragraph
        word_counts = Counter(para_words)
        total_words = len(para_words)
        unique_words = len(word_counts)
        if unique_words > 0:
            # Higher repetition = more topical consistency
            consistency = 1 - (unique_words / total_words)
            consistencies.append(consistency)

    return sum(consistencies) / len(consistencies) if consistencies else 0.0


def _compute_discourse_structure_score(paragraphs: list[str], sentences: list[str]) -> float:
    """Compute discourse structure quality score.

    Evaluates whether the text has clear intro/body/conclusion structure.
    This is a heuristic-based approximation.
    """
    if len(paragraphs) < 2:
        return 0.5  # Single paragraph - neutral score

    if len(paragraphs) < 3:
        return 0.6  # Two paragraphs - minimal structure

    # Heuristics for good structure:
    # 1. Multiple paragraphs (✓ if we get here)
    # 2. First paragraph is introduction-like (shorter or similar length)
    # 3. Last paragraph is conclusion-like

    para_lengths = [len(_split_into_sentences(p)) for p in paragraphs]
    mean_length = sum(para_lengths) / len(para_lengths)

    score = 0.5  # Base score

    # Reward having an intro (first paragraph not too long)
    if para_lengths[0] <= mean_length * 1.5:
        score += 0.15

    # Reward having a conclusion (last paragraph exists and is reasonable)
    if para_lengths[-1] <= mean_length * 1.5:
        score += 0.15

    # Reward having body paragraphs
    if len(paragraphs) >= 3:
        score += 0.1

    # Reward reasonable paragraph count (not too fragmented)
    if 3 <= len(paragraphs) <= 10:
        score += 0.1

    return min(score, 1.0)


def compute_cohesion_coherence(text: str, model: str = "en_core_web_sm") -> CohesionCoherenceResult:
    """Compute cohesion and coherence metrics for text.

    This function analyzes how well a text holds together structurally (cohesion)
    and semantically (coherence). These metrics are important for analyzing
    writing quality, readability, and authorial sophistication.

    Related GitHub Issue:
        #22 - Cohesion and Coherence Metrics
        https://github.com/craigtrim/pystylometry/issues/22

    Cohesion metrics:
        - Referential cohesion: pronouns, demonstratives, anaphora
        - Lexical cohesion: word repetition, content word overlap, lexical chains
        - Connective density: discourse markers categorized by type

    Coherence metrics:
        - Adjacent sentence overlap
        - Paragraph topic consistency
        - Mean sentence similarity
        - Discourse structure quality

    References:
        Halliday, M. A. K., & Hasan, R. (1976). Cohesion in English. Longman.
        Graesser, A. C., McNamara, D. S., & Kulikowich, J. M. (2011). Coh-Metrix.

    Args:
        text: Input text to analyze (multi-sentence/paragraph text recommended)
        model: spaCy model name for linguistic analysis (default: "en_core_web_sm")

    Returns:
        CohesionCoherenceResult with all cohesion and coherence metrics

    Raises:
        ImportError: If spaCy is not installed

    Example:
        >>> result = compute_cohesion_coherence('''
        ...     The cat sat on the mat. It was comfortable there.
        ...     The mat was soft and warm. The cat purred contentedly.
        ... ''')
        >>> print(f"Pronoun density: {result.pronoun_density:.2f}")
        >>> print(f"Adjacent overlap: {result.adjacent_sentence_overlap:.3f}")
        >>> print(f"Connective density: {result.connective_density:.2f}")
    """
    check_optional_dependency("spacy", "stylistic (cohesion)")

    import spacy

    # Handle empty text
    if not text or not text.strip():
        return CohesionCoherenceResult(
            pronoun_density=0.0,
            demonstrative_density=0.0,
            anaphora_count=0,
            anaphora_resolution_ratio=1.0,
            word_repetition_ratio=0.0,
            synonym_density=0.0,
            lexical_chain_count=0,
            mean_chain_length=0.0,
            content_word_overlap=0.0,
            connective_density=0.0,
            additive_connective_ratio=0.0,
            adversative_connective_ratio=0.0,
            causal_connective_ratio=0.0,
            temporal_connective_ratio=0.0,
            adjacent_sentence_overlap=0.0,
            paragraph_topic_consistency=0.0,
            mean_sentence_similarity=0.0,
            semantic_coherence_score=0.0,
            paragraph_count=0,
            mean_paragraph_length=0.0,
            discourse_structure_score=0.0,
            metadata={
                "model": model,
                "word_count": 0,
                "sentence_count": 0,
                "pronoun_count": 0,
                "demonstrative_count": 0,
                "connective_counts": {"additive": 0, "adversative": 0, "causal": 0, "temporal": 0},
                "lexical_chains": [],
            },
        )

    # Load spaCy model
    try:
        nlp = spacy.load(model)
    except OSError:
        raise OSError(
            f"spaCy model '{model}' not found. Download it with: python -m spacy download {model}"
        )

    # Process text with spaCy
    doc = nlp(text)

    # Basic counts
    word_count = sum(1 for token in doc if token.is_alpha)
    if word_count == 0:
        return CohesionCoherenceResult(
            pronoun_density=0.0,
            demonstrative_density=0.0,
            anaphora_count=0,
            anaphora_resolution_ratio=1.0,
            word_repetition_ratio=0.0,
            synonym_density=0.0,
            lexical_chain_count=0,
            mean_chain_length=0.0,
            content_word_overlap=0.0,
            connective_density=0.0,
            additive_connective_ratio=0.0,
            adversative_connective_ratio=0.0,
            causal_connective_ratio=0.0,
            temporal_connective_ratio=0.0,
            adjacent_sentence_overlap=0.0,
            paragraph_topic_consistency=0.0,
            mean_sentence_similarity=0.0,
            semantic_coherence_score=0.0,
            paragraph_count=0,
            mean_paragraph_length=0.0,
            discourse_structure_score=0.0,
            metadata={
                "model": model,
                "word_count": 0,
                "sentence_count": 0,
                "pronoun_count": 0,
                "demonstrative_count": 0,
                "connective_counts": {"additive": 0, "adversative": 0, "causal": 0, "temporal": 0},
                "lexical_chains": [],
            },
        )

    # ========== Referential Cohesion ==========

    # Count pronouns
    pronoun_count = sum(1 for token in doc if token.pos_ == "PRON" and token.is_alpha)
    pronoun_density = (pronoun_count / word_count) * 100

    # Count demonstratives
    demonstrative_count = sum(
        1 for token in doc if token.text.lower() in DEMONSTRATIVES and token.is_alpha
    )
    demonstrative_density = (demonstrative_count / word_count) * 100

    # Anaphora metrics
    anaphora_count, anaphora_resolution_ratio = _compute_anaphora_metrics(doc)

    # ========== Lexical Cohesion ==========

    # Split into sentences for sentence-level analysis
    sentences_text = _split_into_sentences(text)
    sentence_count = len(sentences_text)

    # Get content words per sentence using spaCy
    sentences_content_words: list[list[str]] = []
    for sent_text in sentences_text:
        sent_doc = nlp(sent_text)
        content_words = _get_content_words_from_doc(sent_doc)
        sentences_content_words.append(content_words)

    # Word repetition ratio
    word_repetition_ratio = _compute_word_repetition(sentences_content_words)

    # Lexical chains
    lexical_chains = _compute_lexical_chains(sentences_content_words)
    lexical_chain_count = len(lexical_chains)
    mean_chain_length = (
        sum(len(chain) for chain in lexical_chains) / lexical_chain_count
        if lexical_chain_count > 0
        else 0.0
    )

    # Content word overlap between adjacent sentences
    content_word_overlap = _compute_adjacent_overlap(sentences_content_words)

    # Synonym density: simplified as 0 (would require WordNet for true synonyms)
    # This is a placeholder - full implementation would use NLTK WordNet
    synonym_density = 0.0

    # ========== Connectives ==========

    tokens = _tokenize_simple(text)
    connective_counts = _count_connectives(tokens)
    total_connectives = sum(connective_counts.values())
    connective_density = (total_connectives / word_count) * 100 if word_count > 0 else 0.0

    # Connective ratios
    additive_ratio = (
        connective_counts["additive"] / total_connectives if total_connectives > 0 else 0.0
    )
    adversative_ratio = (
        connective_counts["adversative"] / total_connectives if total_connectives > 0 else 0.0
    )
    causal_ratio = connective_counts["causal"] / total_connectives if total_connectives > 0 else 0.0
    temporal_ratio = (
        connective_counts["temporal"] / total_connectives if total_connectives > 0 else 0.0
    )

    # ========== Coherence Measures ==========

    # Adjacent sentence overlap
    adjacent_sentence_overlap = _compute_adjacent_overlap(sentences_content_words)

    # Mean pairwise sentence similarity
    mean_sentence_similarity = _compute_mean_sentence_similarity(sentences_content_words)

    # Paragraphs
    paragraphs = _split_into_paragraphs(text)
    paragraph_count = len(paragraphs)

    # Mean paragraph length (in sentences)
    if paragraph_count > 0:
        para_sentence_counts = [len(_split_into_sentences(p)) for p in paragraphs]
        mean_paragraph_length = sum(para_sentence_counts) / paragraph_count
    else:
        mean_paragraph_length = 0.0

    # Paragraph topic consistency
    paragraphs_content_words = []
    for para in paragraphs:
        para_doc = nlp(para)
        paragraphs_content_words.append(_get_content_words_from_doc(para_doc))
    paragraph_topic_consistency = _compute_paragraph_topic_consistency(paragraphs_content_words)

    # Discourse structure score
    discourse_structure_score = _compute_discourse_structure_score(paragraphs, sentences_text)

    # Composite semantic coherence score (0-1)
    # Weighted combination of coherence metrics
    semantic_coherence_score = (
        0.3 * adjacent_sentence_overlap
        + 0.2 * mean_sentence_similarity
        + 0.2 * paragraph_topic_consistency
        + 0.15 * min(connective_density / 5.0, 1.0)  # Normalize connective density
        + 0.15 * discourse_structure_score
    )
    semantic_coherence_score = min(max(semantic_coherence_score, 0.0), 1.0)

    return CohesionCoherenceResult(
        # Referential cohesion
        pronoun_density=pronoun_density,
        demonstrative_density=demonstrative_density,
        anaphora_count=anaphora_count,
        anaphora_resolution_ratio=anaphora_resolution_ratio,
        # Lexical cohesion
        word_repetition_ratio=word_repetition_ratio,
        synonym_density=synonym_density,
        lexical_chain_count=lexical_chain_count,
        mean_chain_length=mean_chain_length,
        content_word_overlap=content_word_overlap,
        # Connectives
        connective_density=connective_density,
        additive_connective_ratio=additive_ratio,
        adversative_connective_ratio=adversative_ratio,
        causal_connective_ratio=causal_ratio,
        temporal_connective_ratio=temporal_ratio,
        # Coherence
        adjacent_sentence_overlap=adjacent_sentence_overlap,
        paragraph_topic_consistency=paragraph_topic_consistency,
        mean_sentence_similarity=mean_sentence_similarity,
        semantic_coherence_score=semantic_coherence_score,
        # Structural
        paragraph_count=paragraph_count,
        mean_paragraph_length=mean_paragraph_length,
        discourse_structure_score=discourse_structure_score,
        # Metadata
        metadata={
            "model": model,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "pronoun_count": pronoun_count,
            "demonstrative_count": demonstrative_count,
            "connective_counts": connective_counts,
            "total_connectives": total_connectives,
            "lexical_chains": [
                {"word": chain[0] if chain else "", "length": len(chain)}
                for chain in lexical_chains
            ],
            "content_words_per_sentence": [len(s) for s in sentences_content_words],
        },
    )
