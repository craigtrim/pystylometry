"""Part-of-Speech ratio analysis using spaCy."""

from .._types import POSResult
from .._utils import check_optional_dependency


def compute_pos_ratios(text: str, model: str = "en_core_web_sm") -> POSResult:
    """
    Compute Part-of-Speech ratios and lexical density using spaCy.

    Metrics computed:
    - Noun ratio: nouns / total words
    - Verb ratio: verbs / total words
    - Adjective ratio: adjectives / total words
    - Adverb ratio: adverbs / total words
    - Noun-verb ratio: nouns / verbs
    - Adjective-noun ratio: adjectives / nouns
    - Lexical density: (nouns + verbs + adjectives + adverbs) / total words
    - Function word ratio: (determiners + prepositions + conjunctions) / total words

    References:
        Biber, D. (1988). Variation across speech and writing.
        Cambridge University Press.

    Args:
        text: Input text to analyze
        model: spaCy model name (default: "en_core_web_sm")

    Returns:
        POSResult with all POS ratios and metadata

    Raises:
        ImportError: If spaCy is not installed

    Example:
        >>> result = compute_pos_ratios("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Noun ratio: {result.noun_ratio:.3f}")
        >>> print(f"Verb ratio: {result.verb_ratio:.3f}")
        >>> print(f"Lexical density: {result.lexical_density:.3f}")
    """
    check_optional_dependency("spacy", "syntactic")

    import spacy

    # Load spaCy model
    try:
        nlp = spacy.load(model)
    except OSError:
        raise OSError(
            f"spaCy model '{model}' not found. "
            f"Download it with: python -m spacy download {model}"
        )

    # Process text with spaCy
    doc = nlp(text)

    # Count POS tags
    noun_count = 0
    verb_count = 0
    adj_count = 0
    adv_count = 0
    det_count = 0
    adp_count = 0  # Adpositions (prepositions)
    conj_count = 0  # Conjunctions (coordinating and subordinating)
    total_tokens = 0

    for token in doc:
        # Only count alphabetic tokens (skip punctuation, numbers, etc.)
        if not token.is_alpha:
            continue

        total_tokens += 1
        pos = token.pos_

        if pos == "NOUN" or pos == "PROPN":
            noun_count += 1
        elif pos == "VERB":
            verb_count += 1
        elif pos == "ADJ":
            adj_count += 1
        elif pos == "ADV":
            adv_count += 1
        elif pos == "DET":
            det_count += 1
        elif pos == "ADP":
            adp_count += 1
        elif pos in ("CCONJ", "SCONJ"):
            conj_count += 1

    # Handle empty text
    if total_tokens == 0:
        return POSResult(
            noun_ratio=float("nan"),
            verb_ratio=float("nan"),
            adjective_ratio=float("nan"),
            adverb_ratio=float("nan"),
            noun_verb_ratio=float("nan"),
            adjective_noun_ratio=float("nan"),
            lexical_density=float("nan"),
            function_word_ratio=float("nan"),
            metadata={
                "model": model,
                "token_count": 0,
                "noun_count": 0,
                "verb_count": 0,
                "adjective_count": 0,
                "adverb_count": 0,
            },
        )

    # Calculate ratios
    noun_ratio = noun_count / total_tokens
    verb_ratio = verb_count / total_tokens
    adj_ratio = adj_count / total_tokens
    adv_ratio = adv_count / total_tokens

    # Noun-verb ratio (handle division by zero)
    noun_verb_ratio = noun_count / verb_count if verb_count > 0 else float("nan")

    # Adjective-noun ratio (handle division by zero)
    adj_noun_ratio = adj_count / noun_count if noun_count > 0 else float("nan")

    # Lexical density: (content words) / total words
    # Content words = nouns + verbs + adjectives + adverbs
    lexical_words = noun_count + verb_count + adj_count + adv_count
    lexical_density = lexical_words / total_tokens

    # Function word ratio: (determiners + prepositions + conjunctions) / total words
    function_words = det_count + adp_count + conj_count
    function_word_ratio = function_words / total_tokens

    return POSResult(
        noun_ratio=noun_ratio,
        verb_ratio=verb_ratio,
        adjective_ratio=adj_ratio,
        adverb_ratio=adv_ratio,
        noun_verb_ratio=noun_verb_ratio,
        adjective_noun_ratio=adj_noun_ratio,
        lexical_density=lexical_density,
        function_word_ratio=function_word_ratio,
        metadata={
            "model": model,
            "token_count": total_tokens,
            "noun_count": noun_count,
            "verb_count": verb_count,
            "adjective_count": adj_count,
            "adverb_count": adv_count,
            "determiner_count": det_count,
            "adposition_count": adp_count,
            "conjunction_count": conj_count,
        },
    )
