"""Additional readability formulas.

This module provides additional readability metrics beyond the core formulas
(Flesch, SMOG, Gunning Fog, Coleman-Liau, ARI). These formulas offer alternative
approaches to measuring text difficulty and are valuable for cross-validation
and comprehensive readability assessment.

Related GitHub Issues:
    #16 - Additional Readability Formulas
    #27 - Native chunked analysis with Distribution dataclass

Formulas implemented:
    - Dale-Chall: Based on list of 3000 familiar words
    - Linsear Write: Developed for technical writing assessment
    - Fry Readability Graph: Visual graph-based assessment
    - FORCAST: Military formula using only single-syllable words
    - Powers-Sumner-Kearl: Recalibrated Flesch for primary grades

References:
    Dale, E., & Chall, J. S. (1948). A formula for predicting readability.
    Chall, J. S., & Dale, E. (1995). Readability revisited: The new Dale-Chall
        readability formula. Brookline Books.
    Klare, G. R. (1974-1975). Assessing readability. Reading Research Quarterly.
    Fry, E. (1968). A readability formula that saves time. Journal of Reading.
    Caylor, J. S., et al. (1973). Methodologies for determining reading requirements
        of military occupational specialties. Human Resources Research Organization.
    Powers, R. D., Sumner, W. A., & Kearl, B. E. (1958). A recalculation of four
        adult readability formulas. Journal of Educational Psychology.
"""

import math

from .._normalize import normalize_for_readability
from .._types import (
    DaleChallResult,
    Distribution,
    FORCASTResult,
    FryResult,
    LinsearWriteResult,
    PowersSumnerKearlResult,
    chunk_text,
    make_distribution,
)
from .._utils import split_sentences, tokenize
from .syllables import count_syllables

# Dale-Chall List of Familiar Words (subset of ~1200 words)
# GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
# Full Dale-Chall list has 3000 words that 80% of 4th graders understand.
# This is a representative subset covering most common everyday words.
DALE_CHALL_FAMILIAR_WORDS = {
    # Articles, pronouns, determiners
    "a",
    "an",
    "the",
    "this",
    "that",
    "these",
    "those",
    "some",
    "any",
    "all",
    "each",
    "every",
    "both",
    "few",
    "many",
    "much",
    "more",
    "most",
    "other",
    "another",
    "such",
    "what",
    "which",
    "who",
    "whom",
    "whose",
    "whoever",
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
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
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
    "ones",
    "someone",
    "somebody",
    "something",
    "anyone",
    "anybody",
    "anything",
    "everyone",
    "everybody",
    "everything",
    "no",
    "none",
    "nobody",
    "nothing",
    # Conjunctions and prepositions
    "and",
    "or",
    "but",
    "if",
    "when",
    "where",
    "why",
    "how",
    "because",
    "so",
    "for",
    "nor",
    "yet",
    "after",
    "before",
    "while",
    "since",
    "until",
    "unless",
    "though",
    "although",
    "whether",
    "than",
    "as",
    "like",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "about",
    "into",
    "through",
    "over",
    "under",
    "above",
    "below",
    "between",
    "among",
    "against",
    "during",
    "without",
    "within",
    "along",
    "across",
    "behind",
    "beside",
    "near",
    "off",
    "out",
    "up",
    "down",
    "around",
    "past",
    "toward",
    "upon",
    # Common verbs (base, past, -ing, -ed forms included)
    "be",
    "am",
    "is",
    "are",
    "was",
    "were",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "done",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
    "can",
    "could",
    "go",
    "goes",
    "went",
    "gone",
    "going",
    "come",
    "comes",
    "came",
    "coming",
    "make",
    "makes",
    "made",
    "making",
    "get",
    "gets",
    "got",
    "getting",
    "gotten",
    "know",
    "knows",
    "knew",
    "known",
    "knowing",
    "think",
    "thinks",
    "thought",
    "thinking",
    "see",
    "sees",
    "saw",
    "seen",
    "seeing",
    "look",
    "looks",
    "looked",
    "looking",
    "take",
    "takes",
    "took",
    "taken",
    "taking",
    "give",
    "gives",
    "gave",
    "given",
    "giving",
    "find",
    "finds",
    "found",
    "finding",
    "tell",
    "tells",
    "told",
    "telling",
    "ask",
    "asks",
    "asked",
    "asking",
    "work",
    "works",
    "worked",
    "working",
    "seem",
    "seems",
    "seemed",
    "seeming",
    "feel",
    "feels",
    "felt",
    "feeling",
    "try",
    "tries",
    "tried",
    "trying",
    "leave",
    "leaves",
    "left",
    "leaving",
    "call",
    "calls",
    "called",
    "calling",
    "use",
    "uses",
    "used",
    "using",
    "want",
    "wants",
    "wanted",
    "wanting",
    "need",
    "needs",
    "needed",
    "needing",
    "say",
    "says",
    "said",
    "saying",
    "talk",
    "talks",
    "talked",
    "talking",
    "turn",
    "turns",
    "turned",
    "turning",
    "run",
    "runs",
    "ran",
    "running",
    "move",
    "moves",
    "moved",
    "moving",
    "live",
    "lives",
    "lived",
    "living",
    "believe",
    "believes",
    "believed",
    "believing",
    "hold",
    "holds",
    "held",
    "holding",
    "bring",
    "brings",
    "brought",
    "bringing",
    "happen",
    "happens",
    "happened",
    "happening",
    "write",
    "writes",
    "wrote",
    "written",
    "writing",
    "sit",
    "sits",
    "sat",
    "sitting",
    "stand",
    "stands",
    "stood",
    "standing",
    "hear",
    "hears",
    "heard",
    "hearing",
    "let",
    "lets",
    "letting",
    "help",
    "helps",
    "helped",
    "helping",
    "show",
    "shows",
    "showed",
    "shown",
    "showing",
    "play",
    "plays",
    "played",
    "playing",
    "read",
    "reads",
    "reading",
    "change",
    "changes",
    "changed",
    "changing",
    "keep",
    "keeps",
    "kept",
    "keeping",
    "start",
    "starts",
    "started",
    "starting",
    "stop",
    "stops",
    "stopped",
    "stopping",
    "learn",
    "learns",
    "learned",
    "learning",
    "grow",
    "grows",
    "grew",
    "grown",
    "growing",
    "open",
    "opens",
    "opened",
    "opening",
    "close",
    "closes",
    "closed",
    "closing",
    "walk",
    "walks",
    "walked",
    "walking",
    "win",
    "wins",
    "won",
    "winning",
    "begin",
    "begins",
    "began",
    "begun",
    "beginning",
    "end",
    "ends",
    "ended",
    "ending",
    "lose",
    "loses",
    "lost",
    "losing",
    "send",
    "sends",
    "sent",
    "sending",
    "buy",
    "buys",
    "bought",
    "buying",
    "pay",
    "pays",
    "paid",
    "paying",
    "eat",
    "eats",
    "ate",
    "eaten",
    "eating",
    "drink",
    "drinks",
    "drank",
    "drinking",
    "sleep",
    "sleeps",
    "slept",
    "sleeping",
    "wake",
    "wakes",
    "woke",
    "waking",
    "sing",
    "sings",
    "sang",
    "sung",
    "singing",
    "dance",
    "dances",
    "danced",
    "dancing",
    "wait",
    "waits",
    "waited",
    "waiting",
    "stay",
    "stays",
    "stayed",
    "staying",
    "fly",
    "flies",
    "flew",
    "flown",
    "flying",
    "fall",
    "falls",
    "fell",
    "fallen",
    "falling",
    "cut",
    "cuts",
    "cutting",
    "break",
    "breaks",
    "broke",
    "broken",
    "breaking",
    "watch",
    "watches",
    "watched",
    "watching",
    "listen",
    "listens",
    "listened",
    "listening",
    "remember",
    "remembers",
    "remembered",
    "remembering",
    "forget",
    "forgets",
    "forgot",
    "forgotten",
    "forgetting",
    "meet",
    "meets",
    "met",
    "meeting",
    "follow",
    "follows",
    "followed",
    "following",
    "carry",
    "carries",
    "carried",
    "carrying",
    "catch",
    "catches",
    "caught",
    "catching",
    "draw",
    "draws",
    "drew",
    "drawn",
    "drawing",
    "drive",
    "drives",
    "drove",
    "driven",
    "driving",
    "ride",
    "rides",
    "rode",
    "ridden",
    "riding",
    "wear",
    "wears",
    "wore",
    "worn",
    "wearing",
    "pull",
    "pulls",
    "pulled",
    "pulling",
    "push",
    "pushes",
    "pushed",
    "pushing",
    "throw",
    "throws",
    "threw",
    "thrown",
    "throwing",
    "reach",
    "reaches",
    "reached",
    "reaching",
    "pass",
    "passes",
    "passed",
    "passing",
    "shoot",
    "shoots",
    "shot",
    "shooting",
    "rise",
    "rises",
    "rose",
    "risen",
    "rising",
    "blow",
    "blows",
    "blew",
    "blown",
    "blowing",
    "grow",
    "grows",
    "grew",
    "grown",
    "growing",
    "hit",
    "hits",
    "hitting",
    "fight",
    "fights",
    "fought",
    "fighting",
    "die",
    "dies",
    "died",
    "dying",
    "kill",
    "kills",
    "killed",
    "killing",
    "speak",
    "speaks",
    "spoke",
    "spoken",
    "speaking",
    # Common nouns
    "time",
    "times",
    "year",
    "years",
    "day",
    "days",
    "week",
    "weeks",
    "month",
    "months",
    "hour",
    "hours",
    "minute",
    "minutes",
    "second",
    "seconds",
    "morning",
    "afternoon",
    "evening",
    "night",
    "today",
    "yesterday",
    "tomorrow",
    "people",
    "person",
    "man",
    "men",
    "woman",
    "women",
    "child",
    "children",
    "boy",
    "boys",
    "girl",
    "girls",
    "baby",
    "babies",
    "friend",
    "friends",
    "family",
    "families",
    "mother",
    "father",
    "parent",
    "parents",
    "brother",
    "brothers",
    "sister",
    "sisters",
    "son",
    "daughter",
    "place",
    "places",
    "home",
    "house",
    "houses",
    "room",
    "rooms",
    "school",
    "schools",
    "class",
    "classes",
    "student",
    "students",
    "teacher",
    "teachers",
    "way",
    "ways",
    "thing",
    "things",
    "part",
    "parts",
    "group",
    "groups",
    "number",
    "numbers",
    "side",
    "sides",
    "kind",
    "kinds",
    "head",
    "heads",
    "hand",
    "hands",
    "eye",
    "eyes",
    "face",
    "faces",
    "body",
    "bodies",
    "foot",
    "feet",
    "arm",
    "arms",
    "leg",
    "legs",
    "ear",
    "ears",
    "mouth",
    "water",
    "food",
    "air",
    "land",
    "earth",
    "ground",
    "world",
    "country",
    "countries",
    "state",
    "states",
    "city",
    "cities",
    "town",
    "towns",
    "name",
    "names",
    "word",
    "words",
    "line",
    "lines",
    "page",
    "pages",
    "book",
    "books",
    "story",
    "stories",
    "letter",
    "letters",
    "paper",
    "papers",
    "point",
    "points",
    "end",
    "ends",
    "top",
    "bottom",
    "front",
    "back",
    "life",
    "lives",
    "problem",
    "problems",
    "question",
    "questions",
    "answer",
    "answers",
    "work",
    "works",
    "job",
    "jobs",
    "money",
    "door",
    "doors",
    "window",
    "windows",
    "car",
    "cars",
    "road",
    "roads",
    "street",
    "streets",
    "tree",
    "trees",
    "animal",
    "animals",
    "bird",
    "birds",
    "fish",
    "dog",
    "dogs",
    "cat",
    "cats",
    "horse",
    "horses",
    "sea",
    "mountain",
    "mountains",
    "river",
    "rivers",
    "sun",
    "moon",
    "star",
    "stars",
    "sky",
    "cloud",
    "clouds",
    "rain",
    "snow",
    "wind",
    "fire",
    "light",
    "dark",
    "sound",
    "sounds",
    "color",
    "colors",
    "white",
    "black",
    "red",
    "blue",
    "green",
    "yellow",
    "brown",
    "orange",
    "game",
    "games",
    "ball",
    "music",
    "song",
    "songs",
    "picture",
    "pictures",
    "table",
    "tables",
    "chair",
    "chairs",
    "bed",
    "beds",
    "floor",
    "wall",
    "walls",
    "minute",
    "power",
    "war",
    "force",
    "age",
    "care",
    "order",
    "case",
    # Common adjectives
    "good",
    "better",
    "best",
    "bad",
    "worse",
    "worst",
    "big",
    "bigger",
    "biggest",
    "small",
    "smaller",
    "smallest",
    "large",
    "larger",
    "largest",
    "little",
    "less",
    "least",
    "long",
    "longer",
    "longest",
    "short",
    "shorter",
    "shortest",
    "high",
    "higher",
    "highest",
    "low",
    "lower",
    "lowest",
    "old",
    "older",
    "oldest",
    "young",
    "younger",
    "youngest",
    "new",
    "newer",
    "newest",
    "great",
    "greater",
    "greatest",
    "important",
    "right",
    "left",
    "own",
    "other",
    "different",
    "same",
    "next",
    "last",
    "first",
    "second",
    "third",
    "early",
    "earlier",
    "earliest",
    "late",
    "later",
    "latest",
    "easy",
    "easier",
    "easiest",
    "hard",
    "harder",
    "hardest",
    "hot",
    "hotter",
    "hottest",
    "cold",
    "colder",
    "coldest",
    "warm",
    "warmer",
    "warmest",
    "cool",
    "cooler",
    "coolest",
    "fast",
    "faster",
    "fastest",
    "slow",
    "slower",
    "slowest",
    "strong",
    "stronger",
    "strongest",
    "weak",
    "weaker",
    "weakest",
    "happy",
    "happier",
    "happiest",
    "sad",
    "sadder",
    "saddest",
    "nice",
    "nicer",
    "nicest",
    "kind",
    "kinder",
    "kindest",
    "sure",
    "free",
    "full",
    "whole",
    "ready",
    "simple",
    "clear",
    "real",
    "true",
    "certain",
    "public",
    "able",
    "several",
    "open",
    "closed",
    "deep",
    "wide",
    "bright",
    "dark",
    "heavy",
    "light",
    "clean",
    "dirty",
    "wet",
    "dry",
    "soft",
    "hard",
    "quiet",
    "loud",
    "quick",
    "slow",
    "rich",
    "poor",
    "sick",
    "well",
    "dead",
    "alive",
    "empty",
    "busy",
    "pretty",
    "beautiful",
    "ugly",
    # Common adverbs
    "very",
    "too",
    "so",
    "more",
    "most",
    "less",
    "least",
    "well",
    "better",
    "best",
    "just",
    "only",
    "even",
    "still",
    "also",
    "just",
    "now",
    "then",
    "here",
    "there",
    "where",
    "how",
    "when",
    "why",
    "not",
    "never",
    "always",
    "often",
    "sometimes",
    "usually",
    "ever",
    "again",
    "back",
    "away",
    "together",
    "once",
    "twice",
    "soon",
    "today",
    "yesterday",
    "tomorrow",
    "already",
    "almost",
    "enough",
    "quite",
    "rather",
    "really",
    "perhaps",
    "maybe",
    "probably",
    "certainly",
    "surely",
    "yes",
    "no",
    "please",
    "thank",
    "sorry",
    # Numbers
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
    "hundred",
    "thousand",
    "million",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    # Additional common words
    "able",
    "accept",
    "across",
    "act",
    "add",
    "afraid",
    "against",
    "agree",
    "allow",
    "alone",
    "appear",
    "apple",
    "area",
    "arm",
    "arrive",
    "art",
    "aunt",
    "ball",
    "become",
    "believe",
    "belong",
    "boat",
    "build",
    "burn",
    "business",
    "chair",
    "chance",
    "church",
    "clear",
    "climb",
    "clothe",
    "clothes",
    "company",
    "contain",
    "continue",
    "control",
    "cook",
    "corner",
    "cost",
    "count",
    "course",
    "cover",
    "create",
    "cross",
    "crowd",
    "cry",
    "decide",
    "depend",
    "describe",
    "develop",
    "die",
    "direction",
    "discover",
    "doctor",
    "double",
    "drop",
    "during",
    "edge",
    "effect",
    "eight",
    "either",
    "else",
    "enjoy",
    "enough",
    "enter",
    "example",
    "except",
    "excite",
    "expect",
    "explain",
    "express",
    "fact",
    "fair",
    "farm",
    "fear",
    "field",
    "fill",
    "final",
    "fine",
    "finger",
    "finish",
    "flower",
    "force",
    "foreign",
    "forest",
    "form",
    "fresh",
    "front",
    "garden",
    "general",
    "glass",
    "god",
    "gold",
    "hang",
    "hat",
    "hope",
    "hot",
    "idea",
    "include",
    "increase",
    "instead",
    "interest",
    "island",
    "join",
    "laugh",
    "law",
    "lead",
    "lie",
    "lift",
    "list",
    "lock",
    "love",
    "machine",
    "mark",
    "matter",
    "mean",
    "measure",
    "member",
    "mention",
    "middle",
    "mile",
    "mind",
    "miss",
    "moment",
    "nation",
    "natural",
    "nature",
    "necessary",
    "neighbor",
    "notice",
    "object",
    "ocean",
    "offer",
    "office",
    "opinion",
    "paint",
    "pair",
    "party",
    "pattern",
    "period",
    "pick",
    "plan",
    "plant",
    "position",
    "possible",
    "pound",
    "prepare",
    "present",
    "president",
    "press",
    "prince",
    "print",
    "probable",
    "produce",
    "promise",
    "proper",
    "protect",
    "prove",
    "purpose",
    "quarter",
    "queen",
    "question",
    "quick",
    "quiet",
    "race",
    "raise",
    "range",
    "rate",
    "reason",
    "receive",
    "record",
    "region",
    "remain",
    "reply",
    "report",
    "represent",
    "require",
    "rest",
    "result",
    "return",
    "roll",
    "rule",
    "sail",
    "salt",
    "save",
    "science",
    "season",
    "seat",
    "seem",
    "sell",
    "sense",
    "sentence",
    "separate",
    "serve",
    "set",
    "settle",
    "seven",
    "shape",
    "share",
    "ship",
    "shore",
    "sign",
    "silver",
    "single",
    "sir",
    "six",
    "size",
    "skin",
    "soldier",
    "solve",
    "south",
    "space",
    "special",
    "speed",
    "spell",
    "spend",
    "spread",
    "spring",
    "square",
    "step",
    "stone",
    "straight",
    "strange",
    "stream",
    "strength",
    "strike",
    "subject",
    "success",
    "sudden",
    "suffer",
    "suggest",
    "suit",
    "summer",
    "supply",
    "support",
    "suppose",
    "surface",
    "surprise",
    "sweet",
    "swim",
    "system",
    "tail",
    "taste",
    "teach",
    "team",
    "telephone",
    "television",
    "temperature",
    "ten",
    "test",
    "thick",
    "thin",
    "though",
    "thousand",
    "three",
    "tire",
    "total",
    "touch",
    "track",
    "train",
    "travel",
    "trip",
    "trouble",
    "type",
    "uncle",
    "understand",
    "unit",
    "universe",
    "value",
    "various",
    "view",
    "village",
    "visit",
    "voice",
    "vote",
    "wagon",
    "wander",
    "warm",
    "wash",
    "wave",
    "wealth",
    "weather",
    "weight",
    "welcome",
    "west",
    "wheel",
    "wild",
    "wind",
    "winter",
    "wish",
    "wonder",
    "wood",
    "yard",
    "yellow",
}


def _compute_dale_chall_single(text: str) -> tuple[float, int, float, float, dict]:
    """Compute Dale-Chall for a single chunk."""
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return (float("nan"), 0, float("nan"), float("nan"), {"sentence_count": 0, "word_count": 0})

    difficult_words = [w for w in word_tokens if w.lower() not in DALE_CHALL_FAMILIAR_WORDS]
    difficult_word_count = len(difficult_words)
    difficult_word_ratio = difficult_word_count / len(word_tokens)
    difficult_word_pct = difficult_word_ratio * 100
    avg_sentence_length = len(word_tokens) / len(sentences)
    raw_score = 0.1579 * difficult_word_pct + 0.0496 * avg_sentence_length
    adjusted = difficult_word_pct > 5.0
    dale_chall_score = raw_score + 3.6365 if adjusted else raw_score

    return (
        dale_chall_score,
        difficult_word_count,
        difficult_word_ratio,
        avg_sentence_length,
        {
            "sentence_count": len(sentences),
            "word_count": len(word_tokens),
            "adjusted": adjusted,
            "raw_score": raw_score,
            "difficult_word_pct": difficult_word_pct,
        },
    )


def _get_dale_chall_grade_level(score: float) -> str:
    """Map Dale-Chall score to grade level."""
    if math.isnan(score):
        return "Unknown"
    if score < 5.0:
        return "4 and below"
    elif score < 6.0:
        return "5-6"
    elif score < 7.0:
        return "7-8"
    elif score < 8.0:
        return "9-10"
    elif score < 9.0:
        return "11-12"
    elif score < 10.0:
        return "College"
    else:
        return "College Graduate"


def compute_dale_chall(text: str, chunk_size: int = 1000) -> DaleChallResult:
    """
    Compute Dale-Chall Readability Formula.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Formula:
        Raw Score = 0.1579 * (difficult_words_pct) + 0.0496 * (avg_sentence_length)

        If difficult_words_pct > 5%:
            Adjusted Score = Raw Score + 3.6365

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        DaleChallResult with dale_chall_score, grade_level, distributions, and metadata

    Example:
        >>> result = compute_dale_chall("Long text here...", chunk_size=1000)
        >>> result.dale_chall_score  # Mean across chunks
        7.3
        >>> result.dale_chall_score_dist.std  # Variance reveals fingerprint
        0.5
    """
    chunks = chunk_text(text, chunk_size)
    score_values = []
    ratio_values = []
    sent_len_values = []
    total_difficult = 0
    total_words = 0
    total_sentences = 0

    for chunk in chunks:
        sc, diff_cnt, diff_rat, sent_len, meta = _compute_dale_chall_single(chunk)
        if not math.isnan(sc):
            score_values.append(sc)
            ratio_values.append(diff_rat)
            sent_len_values.append(sent_len)
        total_difficult += diff_cnt
        total_words += meta.get("word_count", 0)
        total_sentences += meta.get("sentence_count", 0)

    if not score_values:
        empty_dist = Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
        return DaleChallResult(
            dale_chall_score=float("nan"),
            grade_level="Unknown",
            difficult_word_count=0,
            difficult_word_ratio=float("nan"),
            avg_sentence_length=float("nan"),
            total_words=0,
            dale_chall_score_dist=empty_dist,
            difficult_word_ratio_dist=empty_dist,
            avg_sentence_length_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                "sentence_count": 0,
                "raw_score": float("nan"),
                "adjusted": False,
                "difficult_word_pct": float("nan"),
                "reliable": False,
            },
        )

    score_dist = make_distribution(score_values)
    ratio_dist = make_distribution(ratio_values)
    sent_len_dist = make_distribution(sent_len_values)

    # Calculate overall raw score and adjusted status for metadata
    overall_difficult_pct = (total_difficult / total_words * 100) if total_words > 0 else 0.0
    overall_raw_score = 0.1579 * overall_difficult_pct + 0.0496 * sent_len_dist.mean
    overall_adjusted = overall_difficult_pct > 5.0

    return DaleChallResult(
        dale_chall_score=score_dist.mean,
        grade_level=_get_dale_chall_grade_level(score_dist.mean),
        difficult_word_count=total_difficult,
        difficult_word_ratio=ratio_dist.mean,
        avg_sentence_length=sent_len_dist.mean,
        total_words=total_words,
        dale_chall_score_dist=score_dist,
        difficult_word_ratio_dist=ratio_dist,
        avg_sentence_length_dist=sent_len_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "sentence_count": total_sentences,
            "raw_score": overall_raw_score,
            "adjusted": overall_adjusted,
            "difficult_word_pct": overall_difficult_pct,
            "total_sentence_count": total_sentences,
            "total_word_count": total_words,
            "total_difficult_word_count": total_difficult,
            "reliable": total_words >= 100,
        },
    )


def _compute_linsear_single(text: str) -> tuple[float, float, int, int, float, dict]:
    """Compute Linsear Write for a single chunk."""
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            0,
            0,
            float("nan"),
            {"sentence_count": 0, "word_count": 0},
        )

    easy_word_count = sum(1 for w in word_tokens if count_syllables(w) <= 2)
    hard_word_count = len(word_tokens) - easy_word_count
    weighted_sum = easy_word_count + hard_word_count * 3
    raw_score = weighted_sum / len(sentences)
    grade_level_raw = round(raw_score / 2) if raw_score > 20 else round((raw_score - 2) / 2)
    grade_level = max(0.0, float(grade_level_raw))
    avg_sentence_length = len(word_tokens) / len(sentences)

    return (
        raw_score,
        grade_level,
        easy_word_count,
        hard_word_count,
        avg_sentence_length,
        {"sentence_count": len(sentences), "word_count": len(word_tokens)},
    )


def compute_linsear_write(text: str, chunk_size: int = 1000) -> LinsearWriteResult:
    """
    Compute Linsear Write Readability Formula.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        LinsearWriteResult with score, grade_level, distributions, and metadata

    Example:
        >>> result = compute_linsear_write("Long text here...", chunk_size=1000)
        >>> result.linsear_score  # Mean across chunks
        11.3
    """
    chunks = chunk_text(text, chunk_size)
    score_values = []
    grade_values = []
    sent_len_values = []
    total_easy = 0
    total_hard = 0
    total_words = 0

    for chunk in chunks:
        sc, gr, easy, hard, sent_len, meta = _compute_linsear_single(chunk)
        if not math.isnan(sc):
            score_values.append(sc)
            grade_values.append(gr)
            sent_len_values.append(sent_len)
        total_easy += easy
        total_hard += hard
        total_words += meta.get("word_count", 0)

    if not score_values:
        empty_dist = Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
        return LinsearWriteResult(
            linsear_score=float("nan"),
            grade_level=float("nan"),
            easy_word_count=0,
            hard_word_count=0,
            avg_sentence_length=float("nan"),
            linsear_score_dist=empty_dist,
            grade_level_dist=empty_dist,
            avg_sentence_length_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"total_words": 0, "reliable": False},
        )

    score_dist = make_distribution(score_values)
    grade_dist = make_distribution(grade_values)
    sent_len_dist = make_distribution(sent_len_values)

    return LinsearWriteResult(
        linsear_score=score_dist.mean,
        grade_level=grade_dist.mean,
        easy_word_count=total_easy,
        hard_word_count=total_hard,
        avg_sentence_length=sent_len_dist.mean,
        linsear_score_dist=score_dist,
        grade_level_dist=grade_dist,
        avg_sentence_length_dist=sent_len_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={"total_words": total_words, "reliable": total_words >= 100},
    )


def _get_fry_grade_level(avg_sent_len: float, avg_syl_100: float) -> tuple[str, str]:
    """Get Fry grade level and zone from coordinates."""
    if math.isnan(avg_sent_len) or math.isnan(avg_syl_100):
        return ("Unknown", "invalid")

    if avg_syl_100 < 125:
        if avg_sent_len < 7:
            grade, zone = "1", "valid"
        elif avg_sent_len < 11:
            grade, zone = "2", "valid"
        else:
            grade, zone = "3", "valid"
    elif avg_syl_100 < 135:
        if avg_sent_len < 8:
            grade, zone = "2", "valid"
        elif avg_sent_len < 12:
            grade, zone = "3", "valid"
        else:
            grade, zone = "4", "valid"
    elif avg_syl_100 < 145:
        if avg_sent_len < 9:
            grade, zone = "3", "valid"
        elif avg_sent_len < 13:
            grade, zone = "5", "valid"
        else:
            grade, zone = "6", "valid"
    elif avg_syl_100 < 155:
        if avg_sent_len < 10:
            grade, zone = "4", "valid"
        elif avg_sent_len < 14:
            grade, zone = "7", "valid"
        else:
            grade, zone = "8", "valid"
    elif avg_syl_100 < 165:
        if avg_sent_len < 12:
            grade, zone = "6", "valid"
        elif avg_sent_len < 16:
            grade, zone = "9", "valid"
        else:
            grade, zone = "10", "valid"
    elif avg_syl_100 < 175:
        if avg_sent_len < 14:
            grade, zone = "8", "valid"
        elif avg_sent_len < 18:
            grade, zone = "11", "valid"
        else:
            grade, zone = "12", "valid"
    else:
        if avg_sent_len < 16:
            grade, zone = "10", "valid"
        elif avg_sent_len < 20:
            grade, zone = "College", "valid"
        else:
            grade, zone = "College+", "valid"

    if avg_syl_100 > 185 or avg_sent_len > 25:
        zone = "above_graph"
    elif avg_syl_100 < 110:
        zone = "below_graph"

    return (grade, zone)


def _compute_fry_single(text: str) -> tuple[float, float, dict]:
    """Compute Fry for a single chunk. Returns (avg_sent_len, avg_syl_100, meta)."""
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            {"sentence_count": 0, "word_count": 0, "syllable_count": 0, "sample_size": 0},
        )

    sample_size = min(100, len(word_tokens))
    sample_tokens = word_tokens[:sample_size]
    total_syllables = sum(count_syllables(w) for w in sample_tokens)

    word_count_so_far = 0
    sentences_in_sample = 0
    for sent in sentences:
        sent_tokens = normalize_for_readability(tokenize(sent))
        if word_count_so_far + len(sent_tokens) <= sample_size:
            sentences_in_sample += 1
            word_count_so_far += len(sent_tokens)
        else:
            if word_count_so_far < sample_size:
                sentences_in_sample += 1
            break

    sentences_in_sample = max(1, sentences_in_sample)
    avg_sentence_length = sample_size / sentences_in_sample
    avg_syllables_per_100 = (total_syllables / sample_size) * 100

    return (
        avg_sentence_length,
        avg_syllables_per_100,
        {
            "sentence_count": len(sentences),
            "word_count": len(word_tokens),
            "syllable_count": total_syllables,
            "sample_size": sample_size,
        },
    )


def compute_fry(text: str, chunk_size: int = 1000) -> FryResult:
    """
    Compute Fry Readability Graph metrics.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        FryResult with avg_sentence_length, avg_syllables_per_100, distributions, and metadata

    Example:
        >>> result = compute_fry("Long text here...", chunk_size=1000)
        >>> result.avg_sentence_length  # Mean across chunks
        14.3
    """
    chunks = chunk_text(text, chunk_size)
    sent_len_values = []
    syl_100_values = []
    total_words = 0
    total_sentences = 0
    total_syllables = 0

    for chunk in chunks:
        sent_len, syl_100, meta = _compute_fry_single(chunk)
        if not math.isnan(sent_len):
            sent_len_values.append(sent_len)
            syl_100_values.append(syl_100)
        total_words += meta.get("word_count", 0)
        total_sentences += meta.get("sentence_count", 0)
        total_syllables += meta.get("syllable_count", 0)

    if not sent_len_values:
        empty_dist = Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
        return FryResult(
            avg_sentence_length=float("nan"),
            avg_syllables_per_100=float("nan"),
            grade_level="Unknown",
            graph_zone="invalid",
            avg_sentence_length_dist=empty_dist,
            avg_syllables_per_100_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"total_sentences": 0, "total_words": 0, "sample_size": 0, "reliable": False},
        )

    sent_len_dist = make_distribution(sent_len_values)
    syl_100_dist = make_distribution(syl_100_values)
    grade_level, graph_zone = _get_fry_grade_level(sent_len_dist.mean, syl_100_dist.mean)

    # Calculate sample size (min of 100 or total_words for overall)
    sample_size = min(100, total_words)

    return FryResult(
        avg_sentence_length=sent_len_dist.mean,
        avg_syllables_per_100=syl_100_dist.mean,
        grade_level=grade_level,
        graph_zone=graph_zone,
        avg_sentence_length_dist=sent_len_dist,
        avg_syllables_per_100_dist=syl_100_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "total_sentences": total_sentences,
            "total_words": total_words,
            "total_syllables": total_syllables,
            "sample_size": sample_size,
            "reliable": total_words >= 100,
        },
    )


def _compute_forcast_single(text: str) -> tuple[float, float, int, float, dict]:
    """Compute FORCAST for a single chunk."""
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(word_tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            0,
            float("nan"),
            {"word_count": 0, "sample_size": 0, "scaled_n": 0.0},
        )

    sample_size = min(150, len(word_tokens))
    sample_tokens = word_tokens[:sample_size]
    single_syllable_count = sum(1 for w in sample_tokens if count_syllables(w) == 1)
    scaled_n = (
        single_syllable_count * (150 / sample_size) if sample_size < 150 else single_syllable_count
    )
    forcast_score = 20 - (scaled_n / 10)
    grade_level = float(max(0, min(20, round(forcast_score))))
    single_syllable_ratio = single_syllable_count / sample_size

    return (
        forcast_score,
        grade_level,
        single_syllable_count,
        single_syllable_ratio,
        {"word_count": len(word_tokens), "sample_size": sample_size, "scaled_n": scaled_n},
    )


def compute_forcast(text: str, chunk_size: int = 1000) -> FORCASTResult:
    """
    Compute FORCAST Readability Formula.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Formula:
        Grade Level = 20 - (N / 10)
        Where N is the number of single-syllable words in a 150-word sample.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        FORCASTResult with score, grade_level, distributions, and metadata

    Example:
        >>> result = compute_forcast("Long text here...", chunk_size=1000)
        >>> result.forcast_score  # Mean across chunks
        9.7
    """
    chunks = chunk_text(text, chunk_size)
    score_values = []
    grade_values = []
    ratio_values = []
    total_single = 0
    total_words = 0

    for chunk in chunks:
        sc, gr, single_cnt, single_rat, meta = _compute_forcast_single(chunk)
        if not math.isnan(sc):
            score_values.append(sc)
            grade_values.append(gr)
            ratio_values.append(single_rat)
        total_single += single_cnt
        total_words += meta.get("word_count", 0)

    if not score_values:
        empty_dist = Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
        return FORCASTResult(
            forcast_score=float("nan"),
            grade_level=float("nan"),
            single_syllable_ratio=float("nan"),
            single_syllable_count=0,
            total_words=0,
            forcast_score_dist=empty_dist,
            grade_level_dist=empty_dist,
            single_syllable_ratio_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"sample_size": 0, "scaled_n": 0.0, "reliable": False},
        )

    score_dist = make_distribution(score_values)
    grade_dist = make_distribution(grade_values)
    ratio_dist = make_distribution(ratio_values)

    # Calculate overall sample_size and scaled_n for metadata
    overall_sample_size = min(150, total_words)
    overall_scaled_n = (
        total_single * (150 / overall_sample_size)
        if overall_sample_size < 150
        else float(total_single)
    )

    return FORCASTResult(
        forcast_score=score_dist.mean,
        grade_level=grade_dist.mean,
        single_syllable_ratio=ratio_dist.mean,
        single_syllable_count=total_single,
        total_words=total_words,
        forcast_score_dist=score_dist,
        grade_level_dist=grade_dist,
        single_syllable_ratio_dist=ratio_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "sample_size": overall_sample_size,
            "scaled_n": overall_scaled_n,
            "reliable": total_words >= 100,
        },
    )


def _compute_psk_single(text: str) -> tuple[float, float, float, float, int, dict]:
    """Compute PSK for a single chunk."""
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            0,
            {"sentence_count": 0, "word_count": 0},
        )

    total_syllables = sum(count_syllables(w) for w in word_tokens)
    avg_sentence_length = len(word_tokens) / len(sentences)
    avg_syllables_per_word = total_syllables / len(word_tokens)
    psk_score = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029
    grade_level = round(psk_score, 1)

    return (
        psk_score,
        grade_level,
        avg_sentence_length,
        avg_syllables_per_word,
        total_syllables,
        {"sentence_count": len(sentences), "word_count": len(word_tokens)},
    )


def compute_powers_sumner_kearl(text: str, chunk_size: int = 1000) -> PowersSumnerKearlResult:
    """
    Compute Powers-Sumner-Kearl Readability Formula.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Formula:
        Grade Level = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        PowersSumnerKearlResult with score, grade_level, distributions, and metadata

    Example:
        >>> result = compute_powers_sumner_kearl("Long text here...", chunk_size=1000)
        >>> result.psk_score  # Mean across chunks
        2.3
    """
    chunks = chunk_text(text, chunk_size)
    score_values = []
    grade_values = []
    sent_len_values = []
    syl_per_word_values = []
    total_sentences = 0
    total_words = 0
    total_syllables = 0

    for chunk in chunks:
        sc, gr, sent_len, syl_word, syls, meta = _compute_psk_single(chunk)
        if not math.isnan(sc):
            score_values.append(sc)
            grade_values.append(gr)
            sent_len_values.append(sent_len)
            syl_per_word_values.append(syl_word)
        total_sentences += meta.get("sentence_count", 0)
        total_words += meta.get("word_count", 0)
        total_syllables += syls

    if not score_values:
        empty_dist = Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
        return PowersSumnerKearlResult(
            psk_score=float("nan"),
            grade_level=float("nan"),
            avg_sentence_length=float("nan"),
            avg_syllables_per_word=float("nan"),
            total_sentences=0,
            total_words=0,
            total_syllables=0,
            psk_score_dist=empty_dist,
            grade_level_dist=empty_dist,
            avg_sentence_length_dist=empty_dist,
            avg_syllables_per_word_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                "flesch_reading_ease": float("nan"),
                "flesch_kincaid_grade": float("nan"),
                "difference_from_flesch": float("nan"),
                "reliable": False,
            },
        )

    score_dist = make_distribution(score_values)
    grade_dist = make_distribution(grade_values)
    sent_len_dist = make_distribution(sent_len_values)
    syl_word_dist = make_distribution(syl_per_word_values)

    # Compute Flesch metrics for comparison (using the same avg values)
    # Flesch Reading Ease: 206.835 - 1.015 * ASL - 84.6 * ASW
    # Flesch-Kincaid Grade: 0.39 * ASL + 11.8 * ASW - 15.59
    flesch_reading_ease = 206.835 - 1.015 * sent_len_dist.mean - 84.6 * syl_word_dist.mean
    flesch_kincaid_grade = 0.39 * sent_len_dist.mean + 11.8 * syl_word_dist.mean - 15.59
    difference_from_flesch = grade_dist.mean - flesch_kincaid_grade

    return PowersSumnerKearlResult(
        psk_score=score_dist.mean,
        grade_level=grade_dist.mean,
        avg_sentence_length=sent_len_dist.mean,
        avg_syllables_per_word=syl_word_dist.mean,
        total_sentences=total_sentences,
        total_words=total_words,
        total_syllables=total_syllables,
        psk_score_dist=score_dist,
        grade_level_dist=grade_dist,
        avg_sentence_length_dist=sent_len_dist,
        avg_syllables_per_word_dist=syl_word_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "flesch_reading_ease": flesch_reading_ease,
            "flesch_kincaid_grade": flesch_kincaid_grade,
            "difference_from_flesch": difference_from_flesch,
            "reliable": total_words >= 100,
        },
    )
