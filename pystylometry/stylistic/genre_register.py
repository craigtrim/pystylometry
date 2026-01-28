"""Genre and register classification features.

This module extracts features that distinguish between different text types
(academic, journalistic, fiction, legal, etc.) and formality levels.

Related GitHub Issue:
    #23 - Genre and Register Features
    https://github.com/craigtrim/pystylometry/issues/23

References:
    Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
    Biber, D., & Conrad, S. (2009). Register, genre, and style. Cambridge University Press.
    Heylighen, F., & Dewaele, J. M. (1999). Formality of language: Definition,
        measurement and behavioral determinants.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

from .._types import GenreRegisterResult

# =============================================================================
# WORD LISTS
# =============================================================================

# Common Latinate suffixes and prefixes (from Latin/French origin)
# These indicate formal, academic, or technical register
LATINATE_SUFFIXES = frozenset(
    [
        "tion",
        "sion",
        "ment",
        "ity",
        "ence",
        "ance",
        "ious",
        "eous",
        "ible",
        "able",
        "ive",
        "ative",
        "ure",
        "al",
        "ial",
        "ual",
        "ory",
        "ary",
        "ery",
        "ant",
        "ent",
        "ous",
        "uous",
        "ic",
        "ical",
    ]
)

# Common Germanic/Anglo-Saxon words (everyday, informal vocabulary)
# High-frequency words of Old English origin
GERMANIC_COMMON_WORDS = frozenset(
    [
        # Basic verbs
        "be",
        "have",
        "do",
        "go",
        "come",
        "get",
        "make",
        "take",
        "see",
        "know",
        "think",
        "want",
        "give",
        "use",
        "find",
        "tell",
        "ask",
        "work",
        "seem",
        "feel",
        "try",
        "leave",
        "call",
        "keep",
        "let",
        "begin",
        "show",
        "hear",
        "play",
        "run",
        "move",
        "live",
        "believe",
        "hold",
        "bring",
        "happen",
        "write",
        "sit",
        "stand",
        "lose",
        "pay",
        "meet",
        "set",
        "learn",
        "lead",
        "understand",
        "watch",
        "follow",
        "stop",
        "speak",
        "read",
        "spend",
        "grow",
        "open",
        "walk",
        "win",
        "teach",
        "buy",
        "fall",
        "reach",
        "build",
        "sell",
        "wait",
        "cut",
        "kill",
        "sleep",
        "send",
        "stay",
        "rise",
        "drive",
        "drink",
        "break",
        "eat",
        "pull",
        "shake",
        "throw",
        "catch",
        "draw",
        "hit",
        "fight",
        "wear",
        "hang",
        "strike",
        "steal",
        "swim",
        "blow",
        "fly",
        "sing",
        "ring",
        # Basic nouns
        "man",
        "woman",
        "child",
        "day",
        "way",
        "thing",
        "world",
        "life",
        "hand",
        "year",
        "time",
        "work",
        "night",
        "home",
        "word",
        "eye",
        "head",
        "house",
        "room",
        "friend",
        "door",
        "side",
        "water",
        "mother",
        "father",
        "name",
        "week",
        "month",
        "end",
        "heart",
        "mind",
        "body",
        "sun",
        "moon",
        "earth",
        "god",
        "king",
        "land",
        "sea",
        "light",
        "stone",
        "tree",
        "book",
        "town",
        "blood",
        "brother",
        "sister",
        "wife",
        "husband",
        "son",
        "daughter",
        "folk",
        # Basic adjectives
        "good",
        "new",
        "first",
        "last",
        "long",
        "great",
        "little",
        "own",
        "other",
        "old",
        "right",
        "big",
        "high",
        "small",
        "large",
        "young",
        "early",
        "late",
        "whole",
        "true",
        "wrong",
        "strong",
        "dark",
        "bright",
        "deep",
        "free",
        "full",
        "hard",
        "soft",
        "hot",
        "cold",
        "warm",
        "cool",
        "wet",
        "dry",
        "clean",
        "dirty",
        "sharp",
        "dull",
        "thick",
        "thin",
        "wide",
        "narrow",
        "quick",
        "slow",
        "fast",
        "sick",
        "well",
        "dead",
        "alive",
        "rich",
        "poor",
        "sweet",
        "bitter",
        "loud",
        # Basic adverbs and function words
        "up",
        "down",
        "in",
        "out",
        "on",
        "off",
        "over",
        "under",
        "here",
        "there",
        "now",
        "then",
        "when",
        "where",
        "how",
        "why",
        "what",
        "who",
        "which",
        "this",
        "that",
        "these",
        "those",
        "some",
        "any",
        "no",
        "not",
        "all",
        "both",
        "each",
        "every",
        "many",
        "much",
        "few",
        "little",
        "more",
        "most",
        "other",
        "same",
        "such",
        "only",
        "even",
        "also",
        "just",
        "still",
        "yet",
        "already",
        "always",
        "never",
        "often",
        "sometimes",
        "again",
        "back",
        "away",
    ]
)

# Latinate/formal vocabulary (Latin/French origin)
LATINATE_WORDS = frozenset(
    [
        # Academic/formal verbs
        "obtain",
        "acquire",
        "achieve",
        "accomplish",
        "demonstrate",
        "indicate",
        "establish",
        "determine",
        "examine",
        "analyze",
        "evaluate",
        "assess",
        "consider",
        "conclude",
        "suggest",
        "propose",
        "recommend",
        "require",
        "utilize",
        "employ",
        "implement",
        "facilitate",
        "contribute",
        "constitute",
        "represent",
        "comprise",
        "involve",
        "include",
        "exclude",
        "provide",
        "maintain",
        "sustain",
        "retain",
        "contain",
        "attain",
        "pertain",
        "perceive",
        "conceive",
        "receive",
        "deceive",
        "assume",
        "presume",
        "consume",
        "resume",
        "pursue",
        "ensure",
        "assure",
        "observe",
        "preserve",
        "reserve",
        "deserve",
        "conserve",
        "serve",
        "participate",
        "anticipate",
        "communicate",
        "investigate",
        "illustrate",
        "concentrate",
        "eliminate",
        "terminate",
        "dominate",
        # Academic/formal nouns
        "analysis",
        "hypothesis",
        "theory",
        "concept",
        "principle",
        "phenomenon",
        "evidence",
        "conclusion",
        "assumption",
        "implication",
        "significance",
        "consequence",
        "circumstance",
        "occurrence",
        "reference",
        "preference",
        "difference",
        "influence",
        "experience",
        "existence",
        "assistance",
        "resistance",
        "persistence",
        "instance",
        "substance",
        "distance",
        "importance",
        "performance",
        "appearance",
        "maintenance",
        "tolerance",
        "accordance",
        "abundance",
        "guidance",
        "reliance",
        "compliance",
        "institution",
        "organization",
        "administration",
        "consideration",
        "determination",
        "representation",
        "interpretation",
        "implementation",
        "contribution",
        "distribution",
        "constitution",
        "resolution",
        "solution",
        "evolution",
        "revolution",
        "evaluation",
        "situation",
        "association",
        "variation",
        "correlation",
        "examination",
        "investigation",
        "observation",
        # Academic/formal adjectives
        "significant",
        "substantial",
        "considerable",
        "essential",
        "fundamental",
        "primary",
        "secondary",
        "subsequent",
        "previous",
        "initial",
        "final",
        "potential",
        "actual",
        "virtual",
        "crucial",
        "critical",
        "vital",
        "specific",
        "particular",
        "general",
        "universal",
        "individual",
        "personal",
        "professional",
        "traditional",
        "conventional",
        "exceptional",
        "additional",
        "sufficient",
        "efficient",
        "proficient",
        "deficient",
        "magnificent",
        "appropriate",
        "adequate",
        "accurate",
        "precise",
        "explicit",
        "implicit",
        "complex",
        "simple",
        "obvious",
        "apparent",
        "evident",
        "prominent",
        "dominant",
        "relevant",
        "equivalent",
        "frequent",
        "permanent",
    ]
)

# Abstract noun suffixes (indicators of abstract concepts)
ABSTRACT_SUFFIXES = frozenset(
    [
        "ness",
        "ity",
        "ment",
        "tion",
        "sion",
        "ance",
        "ence",
        "dom",
        "hood",
        "ship",
        "ism",
        "acy",
        "age",
        "ure",
        "th",
        "ty",
    ]
)

# Concrete noun categories (physical, tangible things)
CONCRETE_CATEGORIES = frozenset(
    [
        # Body parts
        "head",
        "hand",
        "eye",
        "face",
        "arm",
        "leg",
        "foot",
        "finger",
        "hair",
        "heart",
        "body",
        "skin",
        "bone",
        "blood",
        "mouth",
        "nose",
        "ear",
        "tooth",
        # Natural objects
        "tree",
        "flower",
        "grass",
        "leaf",
        "rock",
        "stone",
        "mountain",
        "river",
        "ocean",
        "sea",
        "lake",
        "sun",
        "moon",
        "star",
        "sky",
        "cloud",
        "rain",
        "snow",
        "wind",
        "fire",
        "water",
        "earth",
        "sand",
        "wood",
        "metal",
        "gold",
        # Man-made objects
        "house",
        "building",
        "room",
        "door",
        "window",
        "wall",
        "floor",
        "roof",
        "table",
        "chair",
        "bed",
        "desk",
        "book",
        "paper",
        "pen",
        "phone",
        "car",
        "bus",
        "train",
        "plane",
        "ship",
        "boat",
        "road",
        "street",
        "bridge",
        "clock",
        "watch",
        "key",
        "knife",
        "cup",
        "plate",
        "glass",
        "bottle",
        # Animals
        "dog",
        "cat",
        "horse",
        "cow",
        "bird",
        "fish",
        "mouse",
        "rat",
        "lion",
        "tiger",
        "bear",
        "wolf",
        "fox",
        "deer",
        "rabbit",
        "snake",
        "frog",
        # Food
        "bread",
        "meat",
        "milk",
        "egg",
        "fruit",
        "apple",
        "orange",
        "rice",
        "potato",
        "vegetable",
        "cheese",
        "butter",
        "sugar",
        "salt",
        "coffee",
        "tea",
        # Clothing
        "shirt",
        "pants",
        "dress",
        "coat",
        "hat",
        "shoe",
        "sock",
        "glove",
    ]
)

# Narrative markers (past tense, action verbs, temporal markers)
NARRATIVE_MARKERS = frozenset(
    [
        # Temporal markers
        "suddenly",
        "then",
        "finally",
        "meanwhile",
        "afterwards",
        "eventually",
        "immediately",
        "soon",
        "later",
        "before",
        "after",
        "once",
        "while",
        # Dialogue tags
        "said",
        "asked",
        "replied",
        "answered",
        "whispered",
        "shouted",
        "cried",
        "exclaimed",
        "muttered",
        "murmured",
        "declared",
        "announced",
        "explained",
        # Motion/action verbs (common in narratives)
        "walked",
        "ran",
        "jumped",
        "fell",
        "stood",
        "sat",
        "looked",
        "watched",
        "turned",
        "moved",
        "came",
        "went",
        "left",
        "arrived",
        "entered",
        "escaped",
        "grabbed",
        "dropped",
        "threw",
        "caught",
        "hit",
        "pushed",
        "pulled",
    ]
)

# Expository markers (present tense, linking verbs, logical connectors)
EXPOSITORY_MARKERS = frozenset(
    [
        # Logical connectors
        "therefore",
        "thus",
        "hence",
        "consequently",
        "furthermore",
        "moreover",
        "however",
        "nevertheless",
        "although",
        "whereas",
        "because",
        "since",
        "indeed",
        "specifically",
        "particularly",
        "generally",
        "typically",
        # Definitional markers
        "defined",
        "means",
        "refers",
        "consists",
        "comprises",
        "includes",
        "involves",
        "represents",
        "indicates",
        "suggests",
        "demonstrates",
        "shows",
        # Structural markers
        "firstly",
        "secondly",
        "thirdly",
        "additionally",
        "similarly",
        "conversely",
        "alternatively",
        "namely",
        "essentially",
    ]
)

# Legal register markers
LEGAL_MARKERS = frozenset(
    [
        "whereas",
        "hereby",
        "herein",
        "hereof",
        "thereof",
        "therein",
        "wherein",
        "forthwith",
        "notwithstanding",
        "pursuant",
        "aforesaid",
        "heretofore",
        "hereafter",
        "henceforth",
        "whereby",
        "whereupon",
        "inasmuch",
        "insofar",
        "shall",
        "aforementioned",
        "undersigned",
        "plaintiff",
        "defendant",
        "jurisdiction",
        "statute",
        "provision",
        "liability",
        "indemnify",
        "covenant",
        "stipulate",
        "terminate",
        "constitute",
        "enforce",
        "comply",
    ]
)

# Academic register markers
ACADEMIC_MARKERS = frozenset(
    [
        "hypothesis",
        "methodology",
        "analysis",
        "findings",
        "conclusion",
        "research",
        "study",
        "evidence",
        "literature",
        "theory",
        "framework",
        "significant",
        "correlation",
        "variable",
        "sample",
        "data",
        "results",
        "furthermore",
        "moreover",
        "however",
        "therefore",
        "consequently",
        "previous",
        "current",
        "subsequent",
        "demonstrate",
        "indicate",
        "suggest",
        "examine",
        "investigate",
        "analyze",
        "evaluate",
        "assess",
        "determine",
    ]
)

# Journalistic register markers
JOURNALISTIC_MARKERS = frozenset(
    [
        "reported",
        "announced",
        "revealed",
        "disclosed",
        "confirmed",
        "denied",
        "claimed",
        "alleged",
        "stated",
        "according",
        "sources",
        "officials",
        "authorities",
        "spokesperson",
        "investigation",
        "breaking",
        "developing",
        "exclusive",
        "update",
        "latest",
        "controversy",
        "scandal",
        "crisis",
    ]
)

# Conversational/informal markers
CONVERSATIONAL_MARKERS = frozenset(
    [
        "yeah",
        "yep",
        "nope",
        "okay",
        "ok",
        "hey",
        "hi",
        "hello",
        "bye",
        "well",
        "like",
        "just",
        "really",
        "actually",
        "basically",
        "literally",
        "totally",
        "gonna",
        "wanna",
        "gotta",
        "kinda",
        "sorta",
        "dunno",
        "lemme",
        "gimme",
        "stuff",
        "thing",
        "things",
        "guy",
        "guys",
        "kids",
        "folks",
        "awesome",
        "cool",
        "nice",
        "great",
        "amazing",
        "terrible",
        "horrible",
        "crazy",
    ]
)

# First person pronouns
FIRST_PERSON_PRONOUNS = frozenset(
    [
        "i",
        "me",
        "my",
        "mine",
        "myself",
        "we",
        "us",
        "our",
        "ours",
        "ourselves",
    ]
)

# Second person pronouns
SECOND_PERSON_PRONOUNS = frozenset(
    [
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
    ]
)

# Third person pronouns
THIRD_PERSON_PRONOUNS = frozenset(
    [
        "he",
        "him",
        "his",
        "himself",
        "she",
        "her",
        "hers",
        "herself",
        "it",
        "its",
        "itself",
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
        "one",
        "oneself",
    ]
)

# Impersonal constructions (start of sentences)
IMPERSONAL_PATTERNS = [
    r"\bit\s+is\b",
    r"\bit\s+was\b",
    r"\bit\s+has\s+been\b",
    r"\bit\s+seems\b",
    r"\bit\s+appears\b",
    r"\bthere\s+is\b",
    r"\bthere\s+are\b",
    r"\bthere\s+was\b",
    r"\bthere\s+were\b",
    r"\bthere\s+has\s+been\b",
    r"\bthere\s+have\s+been\b",
    r"\bone\s+can\b",
    r"\bone\s+may\b",
    r"\bone\s+might\b",
    r"\bone\s+should\b",
    r"\bone\s+must\b",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def _count_latinate_words(tokens: list[str]) -> int:
    """Count words with Latinate characteristics.

    A word is considered Latinate if it:
    1. Is in the explicit Latinate word list, OR
    2. Has a Latinate suffix and is longer than 6 characters

    This heuristic captures formal vocabulary of Latin/French origin.
    """
    count = 0
    for token in tokens:
        if token in LATINATE_WORDS:
            count += 1
        elif len(token) > 6:
            for suffix in LATINATE_SUFFIXES:
                if token.endswith(suffix):
                    count += 1
                    break
    return count


def _count_germanic_words(tokens: list[str]) -> int:
    """Count words with Germanic/Anglo-Saxon characteristics.

    A word is considered Germanic if it:
    1. Is in the explicit Germanic common word list, OR
    2. Is short (4 letters or fewer) and doesn't have Latinate suffix

    This captures everyday vocabulary of Old English origin.
    """
    count = 0
    for token in tokens:
        if token in GERMANIC_COMMON_WORDS:
            count += 1
        elif len(token) <= 4:
            # Short words are typically Germanic
            is_latinate = False
            for suffix in LATINATE_SUFFIXES:
                if token.endswith(suffix):
                    is_latinate = True
                    break
            if not is_latinate:
                count += 1
    return count


def _count_nominalizations(tokens: list[str]) -> int:
    """Count nominalizations (verbs/adjectives turned into nouns).

    Nominalizations are identified by suffixes like -tion, -ment, -ness, -ity.
    These are characteristic of formal, academic writing.

    Reference:
        Biber, D. (1988). Nominalizations are one of the strongest markers
        of informational, formal register.
    """
    count = 0
    nominalization_suffixes = ["tion", "sion", "ment", "ness", "ity", "ance", "ence"]
    for token in tokens:
        if len(token) > 5:  # Avoid false positives on short words
            for suffix in nominalization_suffixes:
                if token.endswith(suffix):
                    count += 1
                    break
    return count


def _count_abstract_nouns(tokens: list[str]) -> int:
    """Count abstract nouns (concepts, ideas, qualities).

    Abstract nouns are identified by:
    1. Suffixes indicating abstract concepts (-ness, -ity, -ism, etc.)
    2. NOT being in the concrete word list
    """
    count = 0
    for token in tokens:
        if len(token) > 4:
            for suffix in ABSTRACT_SUFFIXES:
                if token.endswith(suffix):
                    count += 1
                    break
    return count


def _count_concrete_nouns(tokens: list[str]) -> int:
    """Count concrete nouns (physical, tangible things)."""
    return sum(1 for token in tokens if token in CONCRETE_CATEGORIES)


def _count_pronouns(tokens: list[str]) -> dict[str, int]:
    """Count pronouns by person (first, second, third)."""
    first = sum(1 for t in tokens if t in FIRST_PERSON_PRONOUNS)
    second = sum(1 for t in tokens if t in SECOND_PERSON_PRONOUNS)
    third = sum(1 for t in tokens if t in THIRD_PERSON_PRONOUNS)
    return {"first": first, "second": second, "third": third}


def _count_impersonal_constructions(text: str) -> int:
    """Count impersonal constructions like 'It is...', 'There are...'."""
    count = 0
    text_lower = text.lower()
    for pattern in IMPERSONAL_PATTERNS:
        count += len(re.findall(pattern, text_lower))
    return count


def _count_narrative_markers(tokens: list[str]) -> int:
    """Count markers characteristic of narrative text."""
    return sum(1 for t in tokens if t in NARRATIVE_MARKERS)


def _count_expository_markers(tokens: list[str]) -> int:
    """Count markers characteristic of expository text."""
    return sum(1 for t in tokens if t in EXPOSITORY_MARKERS)


def _count_register_markers(tokens: list[str]) -> dict[str, int]:
    """Count markers for different registers."""
    return {
        "legal": sum(1 for t in tokens if t in LEGAL_MARKERS),
        "academic": sum(1 for t in tokens if t in ACADEMIC_MARKERS),
        "journalistic": sum(1 for t in tokens if t in JOURNALISTIC_MARKERS),
        "conversational": sum(1 for t in tokens if t in CONVERSATIONAL_MARKERS),
    }


def _estimate_dialogue_ratio(text: str) -> float:
    """Estimate the proportion of text that is dialogue.

    Dialogue is detected by quotation marks. This is a heuristic
    that works for most fiction but may miss some edge cases.
    """
    # Find all quoted strings (both single and double quotes)
    double_quoted = re.findall(r'"[^"]*"', text)
    single_quoted = re.findall(r"'[^']*'", text)

    # Calculate total dialogue character count
    dialogue_chars = sum(len(q) for q in double_quoted)
    dialogue_chars += sum(len(q) for q in single_quoted if len(q) > 3)  # Avoid contractions

    total_chars = len(text.strip())
    if total_chars == 0:
        return 0.0

    return min(1.0, dialogue_chars / total_chars)


def _count_quotations(text: str) -> int:
    """Count number of quotation instances."""
    double_quotes = len(re.findall(r'"[^"]*"', text))
    # Only count single quotes that look like actual quotes (longer than contractions)
    single_quotes = len([q for q in re.findall(r"'[^']*'", text) if len(q) > 5])
    return double_quotes + single_quotes


def _detect_passive_voice(text: str) -> int:
    """Detect passive voice constructions using regex patterns.

    Passive voice pattern: form of "be" + past participle
    Examples: "was written", "is considered", "were found"

    This is a heuristic approach. For more accurate detection,
    use spaCy's dependency parser (when available).
    """
    # Pattern: be verb + optional adverb + past participle (-ed, -en, irregular)
    passive_patterns = [
        r"\b(?:is|are|was|were|been|being|be)\s+(?:\w+ly\s+)?(?:\w+ed|written|taken|given|made|done|seen|known|found|told|shown|left|thought|felt|become|begun|broken|chosen|fallen|forgotten|frozen|hidden|spoken|stolen|sworn|woken)\b",
    ]

    count = 0
    text_lower = text.lower()
    for pattern in passive_patterns:
        count += len(re.findall(pattern, text_lower, re.IGNORECASE))

    return count


def _calculate_formality_score(
    latinate_ratio: float,
    nominalization_density: float,
    passive_density: float,
    first_person_ratio: float,
    conversational_count: int,
    word_count: int,
) -> float:
    """Calculate composite formality score (0-100).

    Based on Heylighen & Dewaele (1999) F-score formula, adapted
    for the available features.

    Higher scores indicate more formal text.
    """
    # Base score from Latinate vocabulary (0-40 points)
    latinate_score = min(40.0, latinate_ratio * 100)

    # Nominalization contribution (0-20 points)
    # Typical academic text has 3-6 nominalizations per 100 words
    nom_score = min(20.0, nominalization_density * 4)

    # Passive voice contribution (0-15 points)
    # Typical formal text has 1-3 passives per 100 words
    passive_score = min(15.0, passive_density * 5)

    # First person penalty (reduces formality)
    # High first-person usage is informal
    first_person_penalty = first_person_ratio * 15

    # Conversational marker penalty
    conv_density = (conversational_count / max(1, word_count)) * 100
    conv_penalty = min(20.0, conv_density * 10)

    # Calculate final score
    score = latinate_score + nom_score + passive_score - first_person_penalty - conv_penalty

    # Normalize to 0-100 range
    return max(0.0, min(100.0, score))


def _classify_register(formality_score: float, features: dict[str, float]) -> str:
    """Classify text into register category.

    Registers (from Joos, 1961):
    - frozen: ritualized, unchanging (legal documents, prayers)
    - formal: one-way, no feedback expected (academic papers, reports)
    - consultative: professional discourse (business, technical)
    - casual: relaxed, everyday speech (conversations with friends)
    - intimate: private, personal (close relationships)

    Reference:
        Joos, M. (1961). The Five Clocks. Harcourt, Brace & World.
    """
    legal_markers = features.get("legal_marker_count", 0)

    if formality_score >= 80 or legal_markers >= 3:
        return "frozen"
    elif formality_score >= 60:
        return "formal"
    elif formality_score >= 40:
        return "consultative"
    elif formality_score >= 20:
        return "casual"
    else:
        return "intimate"


def _calculate_genre_scores(
    features: dict[str, Any],
) -> dict[str, float]:
    """Calculate scores for each genre category.

    Returns dict with scores from 0.0 to 1.0 for each genre.
    """
    word_count = max(1, features["word_count"])

    # Academic score
    academic_score = 0.0
    academic_score += min(0.3, features["nominalization_density"] / 10)
    academic_score += min(0.2, features["latinate_ratio"] * 0.5)
    academic_score += min(0.2, features["passive_density"] / 5)
    academic_score += min(0.15, (features["academic_markers"] / word_count) * 20)
    academic_score += min(0.15, features["impersonal_density"] / 3)
    academic_score = min(1.0, academic_score)

    # Journalistic score
    journalistic_score = 0.0
    journalistic_score += min(0.3, (features["journalistic_markers"] / word_count) * 30)
    journalistic_score += min(0.2, features["quotation_density"] / 3)
    journalistic_score += min(
        0.2, 0.5 - abs(features["formality_score"] / 100 - 0.5)
    )  # Middle formality
    journalistic_score += min(0.15, features["third_person_ratio"] * 0.2)
    journalistic_score += 0.15 if features["narrative_expository_ratio"] > 0.3 else 0.0
    journalistic_score = min(1.0, journalistic_score)

    # Fiction score
    fiction_score = 0.0
    fiction_score += min(0.25, features["dialogue_ratio"] * 0.5)
    fiction_score += min(0.25, features["narrative_density"] / 5)
    fiction_score += min(0.2, features["concrete_ratio"] * 0.3)
    fiction_score += min(0.15, features["first_person_ratio"] * 0.2)
    fiction_score += min(0.15, (1.0 - features["latinate_ratio"]) * 0.2)  # Less formal
    fiction_score = min(1.0, fiction_score)

    # Legal score
    legal_score = 0.0
    legal_score += min(0.4, (features["legal_markers"] / word_count) * 50)
    legal_score += min(0.2, features["nominalization_density"] / 8)
    legal_score += min(0.2, features["passive_density"] / 4)
    legal_score += min(0.1, features["latinate_ratio"] * 0.3)
    legal_score += 0.1 if features["formality_score"] > 70 else 0.0
    legal_score = min(1.0, legal_score)

    # Conversational score
    conv_score = 0.0
    conv_score += min(0.3, (features["conversational_markers"] / word_count) * 30)
    conv_score += min(0.2, features["first_person_ratio"] * 0.3)
    conv_score += min(0.2, features["second_person_ratio"] * 0.4)
    conv_score += min(0.15, (1.0 - features["latinate_ratio"]) * 0.25)
    conv_score += min(0.15, (100 - features["formality_score"]) / 100 * 0.2)
    conv_score = min(1.0, conv_score)

    return {
        "academic": academic_score,
        "journalistic": journalistic_score,
        "fiction": fiction_score,
        "legal": legal_score,
        "conversational": conv_score,
    }


def _predict_genre(scores: dict[str, float]) -> tuple[str, float]:
    """Predict the most likely genre and confidence."""
    if not scores:
        return "unknown", 0.0

    best_genre = max(scores, key=scores.get)  # type: ignore[arg-type]
    best_score = scores[best_genre]

    # Calculate confidence based on margin over second-best
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) >= 2:
        margin = sorted_scores[0] - sorted_scores[1]
        confidence = min(1.0, best_score * (1 + margin))
    else:
        confidence = best_score

    return best_genre, confidence


def _count_technical_terms(tokens: list[str], text: str) -> int:
    """Count potential technical/specialized terms.

    Heuristics for technical terms:
    1. Capitalized words not at sentence start
    2. Words with numbers mixed in
    3. Acronyms (all caps, 2-5 letters)
    4. Very long words (>12 chars) that aren't common
    """
    count = 0

    # Count acronyms
    acronyms = re.findall(r"\b[A-Z]{2,5}\b", text)
    count += len(acronyms)

    # Count words with numbers
    alphanumeric = re.findall(r"\b[a-zA-Z]+\d+[a-zA-Z]*\b|\b\d+[a-zA-Z]+\b", text)
    count += len(alphanumeric)

    # Count very long words
    for token in tokens:
        if len(token) > 12 and token not in LATINATE_WORDS:
            count += 1

    return count


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def compute_genre_register(
    text: str,
    model: str = "en_core_web_sm",  # noqa: ARG001 - Reserved for future spaCy integration
) -> GenreRegisterResult:
    """Analyze genre and register features for text classification.

    This function extracts linguistic features that distinguish between
    different text types (academic, journalistic, fiction, legal, conversational)
    and formality levels (frozen, formal, consultative, casual, intimate).

    The analysis is based on Biber's multidimensional approach to register
    variation, combined with Heylighen & Dewaele's formality metrics.

    Related GitHub Issue:
        #23 - Genre and Register Features
        https://github.com/craigtrim/pystylometry/issues/23

    Args:
        text: Input text to analyze.
        model: spaCy model name (reserved for future enhanced analysis).
            Currently unused; analysis uses regex-based heuristics.

    Returns:
        GenreRegisterResult with comprehensive genre and register metrics.

    Features analyzed:
        - Formality markers (Latinate words, nominalizations, passive voice)
        - Personal vs. impersonal style (pronoun distribution)
        - Abstract vs. concrete vocabulary
        - Technical term density
        - Narrative vs. expository markers
        - Dialogue presence and ratio
        - Register classification (frozen to intimate)
        - Genre prediction with confidence scores

    Example:
        >>> result = compute_genre_register("The court hereby finds...")
        >>> print(f"Formality: {result.formality_score:.1f}")
        >>> print(f"Register: {result.register_classification}")
        >>> print(f"Genre: {result.predicted_genre}")

    References:
        Biber, D. (1988). Variation across speech and writing.
            Cambridge University Press.
        Biber, D., & Conrad, S. (2009). Register, genre, and style.
            Cambridge University Press.
        Heylighen, F., & Dewaele, J. M. (1999). Formality of language.
        Joos, M. (1961). The Five Clocks. Harcourt, Brace & World.
    """
    start_time = time.time()

    # Tokenize
    tokens = _tokenize(text)
    word_count = len(tokens)

    # Handle empty text
    if word_count == 0:
        return GenreRegisterResult(
            formality_score=0.0,
            latinate_ratio=0.0,
            nominalization_density=0.0,
            passive_voice_density=0.0,
            first_person_ratio=0.0,
            second_person_ratio=0.0,
            third_person_ratio=0.0,
            impersonal_construction_density=0.0,
            abstract_noun_ratio=0.0,
            concrete_noun_ratio=0.0,
            abstractness_score=0.0,
            technical_term_density=0.0,
            jargon_density=0.0,
            narrative_marker_density=0.0,
            expository_marker_density=0.0,
            narrative_expository_ratio=0.0,
            dialogue_ratio=0.0,
            quotation_density=0.0,
            register_classification="unknown",
            predicted_genre="unknown",
            genre_confidence=0.0,
            academic_score=0.0,
            journalistic_score=0.0,
            fiction_score=0.0,
            legal_score=0.0,
            conversational_score=0.0,
            metadata={
                "word_count": 0,
                "computation_time": time.time() - start_time,
            },
        )

    # Count various features
    latinate_count = _count_latinate_words(tokens)
    germanic_count = _count_germanic_words(tokens)
    nominalization_count = _count_nominalizations(tokens)
    abstract_count = _count_abstract_nouns(tokens)
    concrete_count = _count_concrete_nouns(tokens)
    pronoun_counts = _count_pronouns(tokens)
    impersonal_count = _count_impersonal_constructions(text)
    narrative_count = _count_narrative_markers(tokens)
    expository_count = _count_expository_markers(tokens)
    register_markers = _count_register_markers(tokens)
    passive_count = _detect_passive_voice(text)
    dialogue_ratio = _estimate_dialogue_ratio(text)
    quotation_count = _count_quotations(text)
    technical_count = _count_technical_terms(tokens, text)

    # Calculate ratios and densities
    total_latinate_germanic = latinate_count + germanic_count
    latinate_ratio = (
        latinate_count / total_latinate_germanic if total_latinate_germanic > 0 else 0.0
    )

    nominalization_density = (nominalization_count / word_count) * 100
    passive_density = (passive_count / word_count) * 100
    impersonal_density = (impersonal_count / word_count) * 100

    total_pronouns = sum(pronoun_counts.values())
    first_person_ratio = pronoun_counts["first"] / total_pronouns if total_pronouns > 0 else 0.0
    second_person_ratio = pronoun_counts["second"] / total_pronouns if total_pronouns > 0 else 0.0
    third_person_ratio = pronoun_counts["third"] / total_pronouns if total_pronouns > 0 else 0.0

    total_noun_indicators = abstract_count + concrete_count
    abstract_ratio = abstract_count / total_noun_indicators if total_noun_indicators > 0 else 0.0
    concrete_ratio = concrete_count / total_noun_indicators if total_noun_indicators > 0 else 0.0

    # Abstractness score: weighted by ratio and density
    abstractness_score = abstract_ratio * min(1.0, (abstract_count / word_count) * 20)

    technical_density = (technical_count / word_count) * 100
    # Jargon density approximated by academic + legal markers
    jargon_density = ((register_markers["academic"] + register_markers["legal"]) / word_count) * 100

    narrative_density = (narrative_count / word_count) * 100
    expository_density = (expository_count / word_count) * 100
    narrative_expository_ratio = (
        narrative_density / expository_density if expository_density > 0 else 0.0
    )

    quotation_density = (quotation_count / word_count) * 100

    # Calculate formality score
    formality_score = _calculate_formality_score(
        latinate_ratio=latinate_ratio,
        nominalization_density=nominalization_density,
        passive_density=passive_density,
        first_person_ratio=first_person_ratio,
        conversational_count=register_markers["conversational"],
        word_count=word_count,
    )

    # Build features dict for genre scoring
    features: dict[str, Any] = {
        "word_count": word_count,
        "latinate_ratio": latinate_ratio,
        "nominalization_density": nominalization_density,
        "passive_density": passive_density,
        "formality_score": formality_score,
        "first_person_ratio": first_person_ratio,
        "second_person_ratio": second_person_ratio,
        "third_person_ratio": third_person_ratio,
        "impersonal_density": impersonal_density,
        "abstract_ratio": abstract_ratio,
        "concrete_ratio": concrete_ratio,
        "narrative_density": narrative_density,
        "expository_density": expository_density,
        "narrative_expository_ratio": narrative_expository_ratio,
        "dialogue_ratio": dialogue_ratio,
        "quotation_density": quotation_density,
        "legal_markers": register_markers["legal"],
        "academic_markers": register_markers["academic"],
        "journalistic_markers": register_markers["journalistic"],
        "conversational_markers": register_markers["conversational"],
        "legal_marker_count": register_markers["legal"],
    }

    # Classify register
    register_classification = _classify_register(formality_score, features)

    # Calculate genre scores
    genre_scores = _calculate_genre_scores(features)
    predicted_genre, genre_confidence = _predict_genre(genre_scores)

    computation_time = time.time() - start_time

    return GenreRegisterResult(
        formality_score=formality_score,
        latinate_ratio=latinate_ratio,
        nominalization_density=nominalization_density,
        passive_voice_density=passive_density,
        first_person_ratio=first_person_ratio,
        second_person_ratio=second_person_ratio,
        third_person_ratio=third_person_ratio,
        impersonal_construction_density=impersonal_density,
        abstract_noun_ratio=abstract_ratio,
        concrete_noun_ratio=concrete_ratio,
        abstractness_score=abstractness_score,
        technical_term_density=technical_density,
        jargon_density=jargon_density,
        narrative_marker_density=narrative_density,
        expository_marker_density=expository_density,
        narrative_expository_ratio=narrative_expository_ratio,
        dialogue_ratio=dialogue_ratio,
        quotation_density=quotation_density,
        register_classification=register_classification,
        predicted_genre=predicted_genre,
        genre_confidence=genre_confidence,
        academic_score=genre_scores["academic"],
        journalistic_score=genre_scores["journalistic"],
        fiction_score=genre_scores["fiction"],
        legal_score=genre_scores["legal"],
        conversational_score=genre_scores["conversational"],
        metadata={
            "word_count": word_count,
            "latinate_word_count": latinate_count,
            "germanic_word_count": germanic_count,
            "nominalization_count": nominalization_count,
            "passive_voice_count": passive_count,
            "abstract_noun_count": abstract_count,
            "concrete_noun_count": concrete_count,
            "pronoun_counts": pronoun_counts,
            "impersonal_count": impersonal_count,
            "narrative_marker_count": narrative_count,
            "expository_marker_count": expository_count,
            "register_marker_counts": register_markers,
            "technical_term_count": technical_count,
            "quotation_count": quotation_count,
            "computation_time": computation_time,
        },
    )
