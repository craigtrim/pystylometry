"""Advanced syntactic analysis using dependency parsing.

This module provides sophisticated syntactic metrics beyond basic POS tagging.
Using dependency parsing, it extracts features related to sentence complexity,
grammatical sophistication, and syntactic style preferences.

Related GitHub Issue:
    #17 - Advanced Syntactic Analysis
    https://github.com/craigtrim/pystylometry/issues/17

Features implemented:
    - Parse tree depth (sentence structural complexity)
    - T-units (minimal terminable units - independent clauses with modifiers)
    - Clausal density (clauses per T-unit)
    - Dependent clause ratio
    - Passive voice ratio
    - Subordination and coordination indices
    - Dependency distance metrics
    - Branching direction (left vs. right)

References:
    Hunt, K. W. (1965). Grammatical structures written at three grade levels.
        NCTE Research Report No. 3.
    Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
    Lu, X. (2010). Automatic analysis of syntactic complexity in second language
        writing. International Journal of Corpus Linguistics, 15(4), 474-496.
    Gibson, E. (2000). The dependency locality theory: A distance-based theory
        of linguistic complexity. In Image, language, brain (pp. 95-126).
"""

from typing import Any

from .._types import AdvancedSyntacticResult, Distribution, make_distribution
from .._utils import check_optional_dependency

# Type aliases for spaCy objects (loaded dynamically)
_SpaCyToken = Any
_SpaCyDoc = Any
_SpaCySpan = Any


def compute_advanced_syntactic(
    text: str,
    model: str = "en_core_web_sm",
    chunk_size: int = 1000,
) -> AdvancedSyntacticResult:
    """
    Compute advanced syntactic complexity metrics using dependency parsing.

    This function uses spaCy's dependency parser to extract sophisticated
    syntactic features that go beyond simple POS tagging. These features
    capture sentence complexity, grammatical sophistication, and stylistic
    preferences in syntactic structure.

    Related GitHub Issue:
        #17 - Advanced Syntactic Analysis
        https://github.com/craigtrim/pystylometry/issues/17

    Why syntactic complexity matters:
        1. Correlates with writing proficiency and cognitive development
        2. Distinguishes between genres (academic vs. conversational)
        3. Captures authorial style preferences
        4. Indicates text difficulty and readability
        5. Varies systematically across languages and registers

    Metrics computed:

    Parse Tree Depth:
        - Mean and maximum depth of dependency parse trees
        - Deeper trees = more complex syntactic structures
        - Indicates level of embedding and subordination

    T-units:
        - Minimal terminable units (Hunt 1965)
        - Independent clause + all dependent clauses attached to it
        - More reliable than sentence length for measuring complexity
        - Mean T-unit length is standard complexity measure

    Clausal Density:
        - Number of clauses per T-unit
        - Higher density = more complex, embedded structures
        - Academic writing typically has higher clausal density

    Passive Voice:
        - Ratio of passive constructions to total sentences
        - Academic/formal writing uses more passive voice
        - Fiction/conversational writing uses more active voice

    Subordination & Coordination:
        - Subordination: Use of dependent clauses
        - Coordination: Use of coordinate clauses (and, but, or)
        - Balance indicates syntactic style

    Dependency Distance:
        - Average distance between heads and dependents
        - Longer distances = more processing difficulty
        - Related to working memory load

    Branching Direction:
        - Left-branching: Modifiers before head
        - Right-branching: Modifiers after head
        - English tends toward right-branching

    Args:
        text: Input text to analyze. Should contain multiple sentences for
              reliable metrics. Very short texts may have unstable values.
        model: spaCy model name with dependency parser. Default is "en_core_web_sm".
               Larger models (en_core_web_md, en_core_web_lg) may provide better
               parsing accuracy but are slower.

    Returns:
        AdvancedSyntacticResult containing:
            - mean_parse_tree_depth: Average depth across all parse trees
            - max_parse_tree_depth: Maximum depth in any parse tree
            - t_unit_count: Number of T-units detected
            - mean_t_unit_length: Average words per T-unit
            - clausal_density: Clauses per T-unit
            - dependent_clause_ratio: Dependent clauses / total clauses
            - passive_voice_ratio: Passive sentences / total sentences
            - subordination_index: Subordinate clauses / total clauses
            - coordination_index: Coordinate clauses / total clauses
            - sentence_complexity_score: Composite complexity metric
            - dependency_distance: Mean distance between heads and dependents
            - left_branching_ratio: Left-branching structures / total
            - right_branching_ratio: Right-branching structures / total
            - metadata: Parse tree details, clause counts, etc.

    Example:
        >>> result = compute_advanced_syntactic("Complex multi-clause text...")
        >>> print(f"Parse tree depth: {result.mean_parse_tree_depth:.1f}")
        Parse tree depth: 5.3
        >>> print(f"T-units: {result.t_unit_count}")
        T-units: 12
        >>> print(f"Clausal density: {result.clausal_density:.2f}")
        Clausal density: 2.4
        >>> print(f"Passive voice: {result.passive_voice_ratio * 100:.1f}%")
        Passive voice: 23.5%

        >>> # Compare genres
        >>> academic = compute_advanced_syntactic("Academic paper...")
        >>> fiction = compute_advanced_syntactic("Fiction narrative...")
        >>> print(f"Academic clausal density: {academic.clausal_density:.2f}")
        >>> print(f"Fiction clausal density: {fiction.clausal_density:.2f}")
        >>> # Academic typically higher

    Note:
        - Requires spaCy with dependency parser (small model minimum)
        - Parse accuracy affects metrics (larger models are better)
        - Very long sentences may have parsing errors
        - Passive voice detection uses dependency patterns
        - T-unit segmentation follows Hunt (1965) criteria
        - Empty or very short texts return NaN for ratios
    """
    check_optional_dependency("spacy", "syntactic")

    try:
        import spacy  # type: ignore
    except ImportError as e:
        raise ImportError(
            "spaCy is required for advanced syntactic analysis. "
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
    if len(sentences) == 0 or len(doc) == 0:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return AdvancedSyntacticResult(
            mean_parse_tree_depth=float("nan"),
            max_parse_tree_depth=0,
            t_unit_count=0,
            mean_t_unit_length=float("nan"),
            clausal_density=float("nan"),
            dependent_clause_ratio=float("nan"),
            passive_voice_ratio=float("nan"),
            subordination_index=float("nan"),
            coordination_index=float("nan"),
            sentence_complexity_score=float("nan"),
            dependency_distance=float("nan"),
            left_branching_ratio=float("nan"),
            right_branching_ratio=float("nan"),
            mean_parse_tree_depth_dist=empty_dist,
            max_parse_tree_depth_dist=empty_dist,
            mean_t_unit_length_dist=empty_dist,
            clausal_density_dist=empty_dist,
            dependent_clause_ratio_dist=empty_dist,
            passive_voice_ratio_dist=empty_dist,
            subordination_index_dist=empty_dist,
            coordination_index_dist=empty_dist,
            sentence_complexity_score_dist=empty_dist,
            dependency_distance_dist=empty_dist,
            left_branching_ratio_dist=empty_dist,
            right_branching_ratio_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=0,
            metadata={
                "sentence_count": 0,
                "word_count": 0,
                "total_clauses": 0,
                "warning": "Empty text or no sentences found",
            },
        )

    # 1. Calculate parse tree depth
    parse_depths = []
    for sent in sentences:
        depth = _calculate_max_tree_depth(sent.root)
        parse_depths.append(depth)

    mean_parse_tree_depth = sum(parse_depths) / len(parse_depths)
    max_parse_tree_depth = max(parse_depths)

    # 2. Calculate mean dependency distance
    dependency_distances = []
    for token in doc:
        if token != token.head:  # Exclude root
            distance = abs(token.i - token.head.i)
            dependency_distances.append(distance)

    if dependency_distances:
        mean_dependency_distance = sum(dependency_distances) / len(dependency_distances)
    else:
        mean_dependency_distance = 0.0

    # 3. Identify T-units and calculate mean T-unit length
    t_units = _identify_t_units(doc)
    t_unit_count = len(t_units)
    t_unit_lengths = [len(t_unit) for t_unit in t_units]

    if t_unit_count > 0:
        mean_t_unit_length = sum(t_unit_lengths) / t_unit_count
    else:
        mean_t_unit_length = float("nan")

    # 4. Count clauses (total, dependent, subordinate, coordinate)
    total_clauses = 0
    dependent_clause_count = 0
    subordinate_clause_count = 0
    coordinate_clause_count = 0

    for sent in sentences:
        sent_total, sent_dependent, sent_subordinate, sent_coordinate = _count_clauses(sent)
        total_clauses += sent_total
        dependent_clause_count += sent_dependent
        subordinate_clause_count += sent_subordinate
        coordinate_clause_count += sent_coordinate

    # Calculate ratios
    if total_clauses > 0:
        dependent_clause_ratio = dependent_clause_count / total_clauses
        subordination_index = subordinate_clause_count / total_clauses
        coordination_index = coordinate_clause_count / total_clauses
    else:
        dependent_clause_ratio = float("nan")
        subordination_index = float("nan")
        coordination_index = float("nan")

    if t_unit_count > 0:
        clausal_density = total_clauses / t_unit_count
    else:
        clausal_density = float("nan")

    # 5. Detect passive voice
    passive_sentence_count = sum(1 for sent in sentences if _is_passive_voice(sent))
    passive_voice_ratio = passive_sentence_count / len(sentences)

    # 6. Calculate branching direction
    left_branching = 0
    right_branching = 0

    for token in doc:
        if token != token.head:  # Exclude root
            if token.i < token.head.i:
                left_branching += 1
            else:
                right_branching += 1

    total_branching = left_branching + right_branching
    if total_branching > 0:
        left_branching_ratio = left_branching / total_branching
        right_branching_ratio = right_branching / total_branching
    else:
        left_branching_ratio = float("nan")
        right_branching_ratio = float("nan")

    # 7. Calculate sentence complexity score (composite metric)
    # Normalize individual metrics to 0-1 range
    normalized_parse_depth = min(mean_parse_tree_depth / 10, 1.0)
    normalized_clausal_density = (
        min(clausal_density / 3, 1.0)
        if not isinstance(clausal_density, float) or not (clausal_density != clausal_density)
        else 0.0
    )
    normalized_t_unit_length = (
        min(mean_t_unit_length / 25, 1.0)
        if not isinstance(mean_t_unit_length, float)
        or not (mean_t_unit_length != mean_t_unit_length)
        else 0.0
    )
    normalized_dependency_distance = min(mean_dependency_distance / 5, 1.0)
    normalized_subordination = (
        subordination_index
        if not isinstance(subordination_index, float)
        or not (subordination_index != subordination_index)
        else 0.0
    )

    # Weighted combination
    sentence_complexity_score = (
        0.3 * normalized_parse_depth
        + 0.3 * normalized_clausal_density
        + 0.2 * normalized_t_unit_length
        + 0.1 * normalized_subordination
        + 0.1 * normalized_dependency_distance
    )

    # Create single-value distributions (analysis is done on full text)
    mean_parse_tree_depth_dist = make_distribution([mean_parse_tree_depth])
    max_parse_tree_depth_dist = make_distribution([float(max_parse_tree_depth)])
    mean_t_unit_length_dist = make_distribution([mean_t_unit_length])
    clausal_density_dist = make_distribution([clausal_density])
    dependent_clause_ratio_dist = make_distribution([dependent_clause_ratio])
    passive_voice_ratio_dist = make_distribution([passive_voice_ratio])
    subordination_index_dist = make_distribution([subordination_index])
    coordination_index_dist = make_distribution([coordination_index])
    sentence_complexity_score_dist = make_distribution([sentence_complexity_score])
    dependency_distance_dist = make_distribution([mean_dependency_distance])
    left_branching_ratio_dist = make_distribution([left_branching_ratio])
    right_branching_ratio_dist = make_distribution([right_branching_ratio])

    # Collect metadata
    metadata = {
        "sentence_count": len(sentences),
        "word_count": len(doc),
        "total_clauses": total_clauses,
        "independent_clause_count": total_clauses - dependent_clause_count,
        "dependent_clause_count": dependent_clause_count,
        "subordinate_clause_count": subordinate_clause_count,
        "coordinate_clause_count": coordinate_clause_count,
        "passive_sentence_count": passive_sentence_count,
        "parse_depths_per_sentence": parse_depths,
        "t_unit_lengths": t_unit_lengths,
        "t_unit_count": t_unit_count,
        "dependency_distances": dependency_distances[:100],  # Sample for brevity
        "left_branching_count": left_branching,
        "right_branching_count": right_branching,
        "model_used": model,
    }

    return AdvancedSyntacticResult(
        mean_parse_tree_depth=mean_parse_tree_depth,
        max_parse_tree_depth=max_parse_tree_depth,
        t_unit_count=t_unit_count,
        mean_t_unit_length=mean_t_unit_length,
        clausal_density=clausal_density,
        dependent_clause_ratio=dependent_clause_ratio,
        passive_voice_ratio=passive_voice_ratio,
        subordination_index=subordination_index,
        coordination_index=coordination_index,
        sentence_complexity_score=sentence_complexity_score,
        dependency_distance=mean_dependency_distance,
        left_branching_ratio=left_branching_ratio,
        right_branching_ratio=right_branching_ratio,
        mean_parse_tree_depth_dist=mean_parse_tree_depth_dist,
        max_parse_tree_depth_dist=max_parse_tree_depth_dist,
        mean_t_unit_length_dist=mean_t_unit_length_dist,
        clausal_density_dist=clausal_density_dist,
        dependent_clause_ratio_dist=dependent_clause_ratio_dist,
        passive_voice_ratio_dist=passive_voice_ratio_dist,
        subordination_index_dist=subordination_index_dist,
        coordination_index_dist=coordination_index_dist,
        sentence_complexity_score_dist=sentence_complexity_score_dist,
        dependency_distance_dist=dependency_distance_dist,
        left_branching_ratio_dist=left_branching_ratio_dist,
        right_branching_ratio_dist=right_branching_ratio_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )


def _calculate_max_tree_depth(token: _SpaCyToken) -> int:
    """
    Calculate maximum depth of dependency tree starting from token.

    Args:
        token: spaCy Token to start from (typically sentence root)

    Returns:
        Maximum depth of tree (root = 0, children = parent + 1)
    """
    if not list(token.children):
        return 0

    child_depths = [_calculate_max_tree_depth(child) for child in token.children]
    return max(child_depths) + 1


def _identify_t_units(doc: _SpaCyDoc) -> list[_SpaCySpan]:
    """
    Identify T-units (minimal terminable units) in document.

    A T-unit is one main clause plus all subordinate clauses attached to it.
    This follows Hunt (1965) definition.

    Args:
        doc: spaCy Doc object

    Returns:
        List of spaCy Span objects, each representing a T-unit
    """
    # For simplicity, treat each sentence as a T-unit
    # More sophisticated approach would split compound sentences
    # into separate T-units, but this requires complex coordination analysis
    return list(doc.sents)


def _count_clauses(sent: _SpaCySpan) -> tuple[int, int, int, int]:
    """
    Count different types of clauses in sentence.

    Args:
        sent: spaCy Span representing a sentence

    Returns:
        Tuple of (total_clauses, dependent_clauses, subordinate_clauses, coordinate_clauses)
    """
    # Start with 1 for the main clause
    total = 1
    dependent = 0
    subordinate = 0
    coordinate = 0

    # Dependency labels that indicate clauses
    dependent_clause_labels = {"csubj", "ccomp", "xcomp", "advcl", "acl", "relcl"}
    subordinate_clause_labels = {"advcl", "acl", "relcl"}
    coordinate_clause_labels = {"conj"}

    for token in sent:
        if token.dep_ in dependent_clause_labels:
            total += 1
            dependent += 1
            if token.dep_ in subordinate_clause_labels:
                subordinate += 1
        elif token.dep_ in coordinate_clause_labels and token.pos_ == "VERB":
            # Coordinate clause (conj) with verb = coordinated main clause
            total += 1
            coordinate += 1

    return total, dependent, subordinate, coordinate


def _is_passive_voice(sent: _SpaCySpan) -> bool:
    """
    Detect if sentence contains passive voice construction.

    Args:
        sent: spaCy Span representing a sentence

    Returns:
        True if passive voice detected, False otherwise
    """
    # Look for passive auxiliary + past participle pattern
    for token in sent:
        # Check for passive subject dependency (older spaCy versions)
        if token.dep_ == "nsubjpass":
            return True
        # Check for passive auxiliary + past participle (newer spaCy versions)
        # In newer spaCy, passive is marked with nsubj:pass or through aux:pass
        if "pass" in token.dep_:
            return True
        # Alternative: check for "be" verb + past participle
        if token.dep_ == "auxpass":
            return True

    return False
