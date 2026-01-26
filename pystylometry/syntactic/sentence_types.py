"""Sentence type classification for syntactic analysis.

This module classifies sentences by their grammatical structure (simple, compound,
complex, compound-complex) and communicative function (declarative, interrogative,
imperative, exclamatory). These classifications reveal authorial preferences and
genre-specific patterns.

Related GitHub Issue:
    #18 - Sentence Type Classification
    https://github.com/craigtrim/pystylometry/issues/18

Structural classifications:
    - Simple: One independent clause
    - Compound: Multiple independent clauses joined by coordination
    - Complex: One independent clause + one or more dependent clauses
    - Compound-Complex: Multiple independent + dependent clauses

Functional classifications:
    - Declarative: Makes a statement (ends with period)
    - Interrogative: Asks a question (ends with question mark)
    - Imperative: Gives a command (subject often implicit "you")
    - Exclamatory: Expresses strong emotion (ends with exclamation mark)

References:
    Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
    Huddleston, R., & Pullum, G. K. (2002). The Cambridge Grammar of the English Language.
    Quirk, R., et al. (1985). A Comprehensive Grammar of the English Language. Longman.
"""

from typing import Any

from .._types import Distribution, SentenceTypeResult, make_distribution
from .._utils import check_optional_dependency

# Type alias for spaCy Span (loaded dynamically)
_SpaCySpan = Any


def compute_sentence_types(
    text: str,
    model: str = "en_core_web_sm",
    chunk_size: int = 1000,
) -> SentenceTypeResult:
    """
    Classify sentences by structure and function.

    Analyzes text to determine the distribution of sentence types, both
    structural (based on clause organization) and functional (based on
    communicative purpose). Different authors and genres show characteristic
    patterns in sentence type usage.

    Related GitHub Issue:
        #18 - Sentence Type Classification
        https://github.com/craigtrim/pystylometry/issues/18

    Why sentence types matter:

    Structural complexity:
        - Simple sentences: Direct, clear, easy to process
        - Compound sentences: Coordinate ideas of equal importance
        - Complex sentences: Subordinate ideas, show relationships
        - Compound-complex: Sophisticated, academic style

    Functional diversity:
        - Declarative dominance: Expository/academic writing
        - Interrogative use: Interactive, rhetorical questions
        - Imperative use: Instructional texts, commands
        - Exclamatory use: Emotional, emphatic style

    Genre patterns:
        - Academic: High proportion of complex sentences
        - Fiction: Mix of simple and complex for variety
        - Journalism: Mostly simple and compound for clarity
        - Technical: Predominantly declarative complex sentences

    Structural Classification Algorithm:

    Simple Sentence:
        - Contains exactly one independent clause
        - No dependent clauses
        - Example: "The cat sat on the mat."

    Compound Sentence:
        - Contains two or more independent clauses
        - Joined by coordinating conjunction or semicolon
        - No dependent clauses
        - Example: "I came, and I saw."

    Complex Sentence:
        - Contains one independent clause
        - Plus one or more dependent clauses
        - Example: "When I arrived, I saw her."

    Compound-Complex Sentence:
        - Contains two or more independent clauses
        - Plus one or more dependent clauses
        - Example: "I came when called, and I stayed because I wanted to."

    Functional Classification Algorithm:

    Declarative:
        - Makes a statement
        - Typically ends with period
        - Subject before verb
        - Example: "The sky is blue."

    Interrogative:
        - Asks a question
        - Ends with question mark
        - Often inverted word order or question words
        - Example: "Is the sky blue?"

    Imperative:
        - Gives a command or instruction
        - Subject typically implicit ("you")
        - Often begins with base verb
        - Example: "Look at the sky!"

    Exclamatory:
        - Expresses strong emotion
        - Ends with exclamation mark
        - May have inverted structure
        - Example: "What a blue sky!"

    Args:
        text: Input text to analyze. Should contain multiple sentences for
              meaningful distributions. Single-sentence texts will have ratios
              of 1.0 for one type and 0.0 for others.
        model: spaCy model with dependency parser. Default is "en_core_web_sm".
               Larger models provide better clause detection accuracy.

    Returns:
        SentenceTypeResult containing:

        Structural ratios (sum to 1.0):
            - simple_ratio: Simple sentences / total
            - compound_ratio: Compound sentences / total
            - complex_ratio: Complex sentences / total
            - compound_complex_ratio: Compound-complex / total

        Functional ratios (sum to 1.0):
            - declarative_ratio: Declarative sentences / total
            - interrogative_ratio: Questions / total
            - imperative_ratio: Commands / total
            - exclamatory_ratio: Exclamations / total

        Counts:
            - simple_count, compound_count, complex_count, compound_complex_count
            - declarative_count, interrogative_count, imperative_count, exclamatory_count
            - total_sentences

        Diversity metrics:
            - structural_diversity: Shannon entropy of structural distribution
            - functional_diversity: Shannon entropy of functional distribution

        Metadata:
            - sentence_by_sentence_classifications
            - clause_counts_per_sentence
            - etc.

    Example:
        >>> result = compute_sentence_types("Mix of sentence types here...")
        >>> print(f"Simple: {result.simple_ratio * 100:.1f}%")
        Simple: 35.2%
        >>> print(f"Complex: {result.complex_ratio * 100:.1f}%")
        Complex: 41.3%
        >>> print(f"Questions: {result.interrogative_ratio * 100:.1f}%")
        Questions: 8.5%
        >>> print(f"Structural diversity: {result.structural_diversity:.3f}")
        Structural diversity: 0.847

        >>> # Compare genres
        >>> academic = compute_sentence_types("Academic paper text...")
        >>> fiction = compute_sentence_types("Fiction narrative...")
        >>> print(f"Academic complex: {academic.complex_ratio:.2f}")
        >>> print(f"Fiction simple: {fiction.simple_ratio:.2f}")

    Note:
        - Requires spaCy with dependency parser
        - Clause detection based on dependency relations
        - Coordinating conjunctions: and, but, or, nor, for, yet, so
        - Dependent clause markers: ccomp, advcl, acl, relcl
        - Punctuation used for functional classification
        - Imperative detection uses missing subject + base verb pattern
        - Empty text returns NaN for ratios, 0 for counts
    """
    check_optional_dependency("spacy", "syntactic")

    try:
        import spacy  # type: ignore
    except ImportError as e:
        raise ImportError(
            "spaCy is required for sentence type classification. "
            "Install with: pip install spacy && python -m spacy download en_core_web_sm"
        ) from e

    # Load spaCy model
    try:
        nlp = spacy.load(model)
    except OSError as e:
        raise OSError(
            f"spaCy model '{model}' not found. Download with: python -m spacy download {model}"
        ) from e

    # Parse text
    doc = nlp(text)
    sentences = list(doc.sents)

    # Handle empty text
    if len(sentences) == 0:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return SentenceTypeResult(
            simple_ratio=float("nan"),
            compound_ratio=float("nan"),
            complex_ratio=float("nan"),
            compound_complex_ratio=float("nan"),
            declarative_ratio=float("nan"),
            interrogative_ratio=float("nan"),
            imperative_ratio=float("nan"),
            exclamatory_ratio=float("nan"),
            simple_count=0,
            compound_count=0,
            complex_count=0,
            compound_complex_count=0,
            declarative_count=0,
            interrogative_count=0,
            imperative_count=0,
            exclamatory_count=0,
            total_sentences=0,
            structural_diversity=float("nan"),
            functional_diversity=float("nan"),
            simple_ratio_dist=empty_dist,
            compound_ratio_dist=empty_dist,
            complex_ratio_dist=empty_dist,
            compound_complex_ratio_dist=empty_dist,
            declarative_ratio_dist=empty_dist,
            interrogative_ratio_dist=empty_dist,
            imperative_ratio_dist=empty_dist,
            exclamatory_ratio_dist=empty_dist,
            structural_diversity_dist=empty_dist,
            functional_diversity_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=0,
            metadata={
                "warning": "Empty text or no sentences found",
            },
        )

    # Classify each sentence
    structural_counts = {"simple": 0, "compound": 0, "complex": 0, "compound_complex": 0}
    functional_counts = {"declarative": 0, "interrogative": 0, "imperative": 0, "exclamatory": 0}
    sentence_classifications = []
    clause_counts_per_sentence = []

    for sent in sentences:
        # Count clauses
        independent_count = _count_independent_clauses(sent)
        dependent_count = _count_dependent_clauses(sent)
        clause_counts_per_sentence.append((independent_count, dependent_count))

        # Structural classification
        structural_type = _classify_structural(independent_count, dependent_count)
        structural_counts[structural_type] += 1

        # Functional classification
        functional_type = _classify_functional(sent)
        functional_counts[functional_type] += 1

        # Store classification
        sentence_classifications.append(
            {
                "text": sent.text,
                "structural_type": structural_type,
                "functional_type": functional_type,
                "independent_clauses": independent_count,
                "dependent_clauses": dependent_count,
            }
        )

    # Calculate ratios
    total_sentences = len(sentences)
    simple_ratio = structural_counts["simple"] / total_sentences
    compound_ratio = structural_counts["compound"] / total_sentences
    complex_ratio = structural_counts["complex"] / total_sentences
    compound_complex_ratio = structural_counts["compound_complex"] / total_sentences

    declarative_ratio = functional_counts["declarative"] / total_sentences
    interrogative_ratio = functional_counts["interrogative"] / total_sentences
    imperative_ratio = functional_counts["imperative"] / total_sentences
    exclamatory_ratio = functional_counts["exclamatory"] / total_sentences

    # Calculate diversity metrics
    structural_ratios = [simple_ratio, compound_ratio, complex_ratio, compound_complex_ratio]
    functional_ratios = [
        declarative_ratio,
        interrogative_ratio,
        imperative_ratio,
        exclamatory_ratio,
    ]

    structural_diversity = _calculate_shannon_entropy(structural_ratios)
    functional_diversity = _calculate_shannon_entropy(functional_ratios)

    # Create single-value distributions (sentence analysis is done on full text)
    simple_ratio_dist = make_distribution([simple_ratio])
    compound_ratio_dist = make_distribution([compound_ratio])
    complex_ratio_dist = make_distribution([complex_ratio])
    compound_complex_ratio_dist = make_distribution([compound_complex_ratio])
    declarative_ratio_dist = make_distribution([declarative_ratio])
    interrogative_ratio_dist = make_distribution([interrogative_ratio])
    imperative_ratio_dist = make_distribution([imperative_ratio])
    exclamatory_ratio_dist = make_distribution([exclamatory_ratio])
    structural_diversity_dist = make_distribution([structural_diversity])
    functional_diversity_dist = make_distribution([functional_diversity])

    # Collect metadata
    metadata = {
        "sentence_count": total_sentences,
        "sentence_classifications": sentence_classifications,
        "clause_counts_per_sentence": clause_counts_per_sentence,
        "structural_counts": structural_counts,
        "functional_counts": functional_counts,
        "model_used": model,
    }

    return SentenceTypeResult(
        simple_ratio=simple_ratio,
        compound_ratio=compound_ratio,
        complex_ratio=complex_ratio,
        compound_complex_ratio=compound_complex_ratio,
        declarative_ratio=declarative_ratio,
        interrogative_ratio=interrogative_ratio,
        imperative_ratio=imperative_ratio,
        exclamatory_ratio=exclamatory_ratio,
        simple_count=structural_counts["simple"],
        compound_count=structural_counts["compound"],
        complex_count=structural_counts["complex"],
        compound_complex_count=structural_counts["compound_complex"],
        declarative_count=functional_counts["declarative"],
        interrogative_count=functional_counts["interrogative"],
        imperative_count=functional_counts["imperative"],
        exclamatory_count=functional_counts["exclamatory"],
        total_sentences=total_sentences,
        structural_diversity=structural_diversity,
        functional_diversity=functional_diversity,
        simple_ratio_dist=simple_ratio_dist,
        compound_ratio_dist=compound_ratio_dist,
        complex_ratio_dist=complex_ratio_dist,
        compound_complex_ratio_dist=compound_complex_ratio_dist,
        declarative_ratio_dist=declarative_ratio_dist,
        interrogative_ratio_dist=interrogative_ratio_dist,
        imperative_ratio_dist=imperative_ratio_dist,
        exclamatory_ratio_dist=exclamatory_ratio_dist,
        structural_diversity_dist=structural_diversity_dist,
        functional_diversity_dist=functional_diversity_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )


def _count_independent_clauses(sent: _SpaCySpan) -> int:
    """
    Count independent clauses in a sentence.

    Independent clauses are:
    1. The root clause (always 1)
    2. Coordinated clauses (conj with VERB POS and cc child)

    Args:
        sent: spaCy Span representing a sentence

    Returns:
        Number of independent clauses
    """
    count = 1  # Always start with root clause

    for token in sent:
        # Coordinated independent clause
        if token.dep_ == "conj" and token.pos_ == "VERB":
            # Check if coordinating conjunction present
            if any(child.dep_ == "cc" for child in token.head.children):
                count += 1

    return count


def _count_dependent_clauses(sent: _SpaCySpan) -> int:
    """
    Count dependent clauses in a sentence.

    Dependent clauses are identified by dependency labels:
    - ccomp: clausal complement
    - advcl: adverbial clause
    - acl: adnominal clause
    - relcl: relative clause
    - xcomp: open clausal complement (sometimes)

    Args:
        sent: spaCy Span representing a sentence

    Returns:
        Number of dependent clauses
    """
    dependent_labels = {"ccomp", "advcl", "acl", "relcl", "xcomp"}
    count = sum(1 for token in sent if token.dep_ in dependent_labels)
    return count


def _classify_structural(independent: int, dependent: int) -> str:
    """
    Classify sentence structure based on clause counts.

    Args:
        independent: Number of independent clauses
        dependent: Number of dependent clauses

    Returns:
        One of: "simple", "compound", "complex", "compound_complex"
    """
    if independent == 1 and dependent == 0:
        return "simple"
    elif independent >= 2 and dependent == 0:
        return "compound"
    elif independent == 1 and dependent >= 1:
        return "complex"
    elif independent >= 2 and dependent >= 1:
        return "compound_complex"
    else:
        # Fallback (shouldn't happen with valid counts)
        return "simple"


def _classify_functional(sent: _SpaCySpan) -> str:
    """
    Classify sentence function based on punctuation and structure.

    Args:
        sent: spaCy Span representing a sentence

    Returns:
        One of: "declarative", "interrogative", "imperative", "exclamatory"
    """
    # Get last token for punctuation
    last_token = sent[-1]

    # Check for question mark (interrogative)
    if last_token.text == "?":
        return "interrogative"

    # Check for exclamation mark
    if last_token.text == "!":
        # Could be imperative or exclamatory
        # Check if imperative structure
        if _is_imperative_structure(sent):
            return "imperative"
        return "exclamatory"

    # Check for imperative structure (missing subject + base verb)
    if _is_imperative_structure(sent):
        return "imperative"

    # Default: declarative
    return "declarative"


def _is_imperative_structure(sent: _SpaCySpan) -> bool:
    """
    Check if sentence has imperative structure.

    Imperatives typically:
    - Missing nominal subject (nsubj)
    - Root verb is base form (VB) or imperative

    Args:
        sent: spaCy Span representing a sentence

    Returns:
        True if imperative structure detected
    """
    # Check for nominal subject
    has_nominal_subject = any(token.dep_ == "nsubj" for token in sent)

    # Get root verb
    root_verb = sent.root

    # If no nominal subject and root is a verb
    if not has_nominal_subject and root_verb.pos_ == "VERB":
        # Check if root is base form (VB) or present tense without subject
        if root_verb.tag_ in {"VB", "VBP"}:
            return True

    return False


def _calculate_shannon_entropy(probabilities: list[float]) -> float:
    """
    Calculate Shannon entropy for a probability distribution.

    H = -sum(p * log2(p)) for p > 0

    Args:
        probabilities: List of probabilities (should sum to 1.0)

    Returns:
        Shannon entropy in bits (0.0 to log2(n) where n is number of categories)
    """
    import math

    # Filter out zero probabilities (log(0) undefined)
    non_zero_probs = [p for p in probabilities if p > 0]

    if not non_zero_probs:
        return 0.0

    # Calculate entropy
    entropy = -sum(p * math.log2(p) for p in non_zero_probs)

    return entropy
