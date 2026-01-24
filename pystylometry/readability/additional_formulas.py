"""Additional readability formulas.

This module provides additional readability metrics beyond the core formulas
(Flesch, SMOG, Gunning Fog, Coleman-Liau, ARI). These formulas offer alternative
approaches to measuring text difficulty and are valuable for cross-validation
and comprehensive readability assessment.

Related GitHub Issue:
    #16 - Additional Readability Formulas
    https://github.com/craigtrim/pystylometry/issues/16

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

from .._normalize import normalize_for_readability
from .._types import (
    DaleChallResult,
    FORCASTResult,
    FryResult,
    LinsearWriteResult,
    PowersSumnerKearlResult,
)
from .._utils import split_sentences, tokenize
from .syllables import count_syllables


# Dale-Chall List of Familiar Words (subset of ~1200 words)
# GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
# Full Dale-Chall list has 3000 words that 80% of 4th graders understand.
# This is a representative subset covering most common everyday words.
DALE_CHALL_FAMILIAR_WORDS = {
    # Articles, pronouns, determiners
    "a", "an", "the", "this", "that", "these", "those", "some", "any", "all",
    "each", "every", "both", "few", "many", "much", "more", "most", "other",
    "another", "such", "what", "which", "who", "whom", "whose", "whoever",
    "i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "one", "ones", "someone", "somebody", "something", "anyone", "anybody", "anything",
    "everyone", "everybody", "everything", "no", "none", "nobody", "nothing",

    # Conjunctions and prepositions
    "and", "or", "but", "if", "when", "where", "why", "how", "because", "so",
    "for", "nor", "yet", "after", "before", "while", "since", "until", "unless",
    "though", "although", "whether", "than", "as", "like",
    "of", "to", "in", "on", "at", "by", "with", "from", "about", "into",
    "through", "over", "under", "above", "below", "between", "among", "against",
    "during", "without", "within", "along", "across", "behind", "beside", "near",
    "off", "out", "up", "down", "around", "past", "toward", "upon",

    # Common verbs (base, past, -ing, -ed forms included)
    "be", "am", "is", "are", "was", "were", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "done",
    "will", "would", "shall", "should", "may", "might", "must", "can", "could",
    "go", "goes", "went", "gone", "going", "come", "comes", "came", "coming",
    "make", "makes", "made", "making", "get", "gets", "got", "getting", "gotten",
    "know", "knows", "knew", "known", "knowing",
    "think", "thinks", "thought", "thinking",
    "see", "sees", "saw", "seen", "seeing", "look", "looks", "looked", "looking",
    "take", "takes", "took", "taken", "taking", "give", "gives", "gave", "given", "giving",
    "find", "finds", "found", "finding", "tell", "tells", "told", "telling",
    "ask", "asks", "asked", "asking", "work", "works", "worked", "working",
    "seem", "seems", "seemed", "seeming", "feel", "feels", "felt", "feeling",
    "try", "tries", "tried", "trying", "leave", "leaves", "left", "leaving",
    "call", "calls", "called", "calling", "use", "uses", "used", "using",
    "want", "wants", "wanted", "wanting", "need", "needs", "needed", "needing",
    "say", "says", "said", "saying", "talk", "talks", "talked", "talking",
    "turn", "turns", "turned", "turning", "run", "runs", "ran", "running",
    "move", "moves", "moved", "moving", "live", "lives", "lived", "living",
    "believe", "believes", "believed", "believing",
    "hold", "holds", "held", "holding", "bring", "brings", "brought", "bringing",
    "happen", "happens", "happened", "happening",
    "write", "writes", "wrote", "written", "writing",
    "sit", "sits", "sat", "sitting", "stand", "stands", "stood", "standing",
    "hear", "hears", "heard", "hearing", "let", "lets", "letting",
    "help", "helps", "helped", "helping", "show", "shows", "showed", "shown", "showing",
    "play", "plays", "played", "playing", "read", "reads", "reading",
    "change", "changes", "changed", "changing", "keep", "keeps", "kept", "keeping",
    "start", "starts", "started", "starting", "stop", "stops", "stopped", "stopping",
    "learn", "learns", "learned", "learning", "grow", "grows", "grew", "grown", "growing",
    "open", "opens", "opened", "opening", "close", "closes", "closed", "closing",
    "walk", "walks", "walked", "walking", "win", "wins", "won", "winning",
    "begin", "begins", "began", "begun", "beginning", "end", "ends", "ended", "ending",
    "lose", "loses", "lost", "losing", "send", "sends", "sent", "sending",
    "buy", "buys", "bought", "buying", "pay", "pays", "paid", "paying",
    "eat", "eats", "ate", "eaten", "eating", "drink", "drinks", "drank", "drinking",
    "sleep", "sleeps", "slept", "sleeping", "wake", "wakes", "woke", "waking",
    "sing", "sings", "sang", "sung", "singing", "dance", "dances", "danced", "dancing",
    "wait", "waits", "waited", "waiting", "stay", "stays", "stayed", "staying",
    "fly", "flies", "flew", "flown", "flying", "fall", "falls", "fell", "fallen", "falling",
    "cut", "cuts", "cutting", "break", "breaks", "broke", "broken", "breaking",
    "watch", "watches", "watched", "watching", "listen", "listens", "listened", "listening",
    "remember", "remembers", "remembered", "remembering",
    "forget", "forgets", "forgot", "forgotten", "forgetting",
    "meet", "meets", "met", "meeting", "follow", "follows", "followed", "following",
    "carry", "carries", "carried", "carrying", "catch", "catches", "caught", "catching",
    "draw", "draws", "drew", "drawn", "drawing", "drive", "drives", "drove", "driven", "driving",
    "ride", "rides", "rode", "ridden", "riding", "wear", "wears", "wore", "worn", "wearing",
    "pull", "pulls", "pulled", "pulling", "push", "pushes", "pushed", "pushing",
    "throw", "throws", "threw", "thrown", "throwing",
    "reach", "reaches", "reached", "reaching", "pass", "passes", "passed", "passing",
    "shoot", "shoots", "shot", "shooting", "rise", "rises", "rose", "risen", "rising",
    "blow", "blows", "blew", "blown", "blowing", "grow", "grows", "grew", "grown", "growing",
    "hit", "hits", "hitting", "fight", "fights", "fought", "fighting",
    "die", "dies", "died", "dying", "kill", "kills", "killed", "killing",
    "speak", "speaks", "spoke", "spoken", "speaking",

    # Common nouns
    "time", "times", "year", "years", "day", "days", "week", "weeks",
    "month", "months", "hour", "hours", "minute", "minutes", "second", "seconds",
    "morning", "afternoon", "evening", "night", "today", "yesterday", "tomorrow",
    "people", "person", "man", "men", "woman", "women", "child", "children",
    "boy", "boys", "girl", "girls", "baby", "babies", "friend", "friends",
    "family", "families", "mother", "father", "parent", "parents",
    "brother", "brothers", "sister", "sisters", "son", "daughter",
    "place", "places", "home", "house", "houses", "room", "rooms",
    "school", "schools", "class", "classes", "student", "students", "teacher", "teachers",
    "way", "ways", "thing", "things", "part", "parts", "group", "groups",
    "number", "numbers", "side", "sides", "kind", "kinds", "head", "heads",
    "hand", "hands", "eye", "eyes", "face", "faces", "body", "bodies",
    "foot", "feet", "arm", "arms", "leg", "legs", "ear", "ears", "mouth",
    "water", "food", "air", "land", "earth", "ground", "world",
    "country", "countries", "state", "states", "city", "cities", "town", "towns",
    "name", "names", "word", "words", "line", "lines", "page", "pages",
    "book", "books", "story", "stories", "letter", "letters", "paper", "papers",
    "point", "points", "end", "ends", "top", "bottom", "front", "back",
    "life", "lives", "problem", "problems", "question", "questions", "answer", "answers",
    "work", "works", "job", "jobs", "money", "door", "doors", "window", "windows",
    "car", "cars", "road", "roads", "street", "streets", "tree", "trees",
    "animal", "animals", "bird", "birds", "fish", "dog", "dogs", "cat", "cats",
    "horse", "horses", "sea", "mountain", "mountains", "river", "rivers",
    "sun", "moon", "star", "stars", "sky", "cloud", "clouds", "rain", "snow",
    "wind", "fire", "light", "dark", "sound", "sounds", "color", "colors",
    "white", "black", "red", "blue", "green", "yellow", "brown", "orange",
    "game", "games", "ball", "music", "song", "songs", "picture", "pictures",
    "table", "tables", "chair", "chairs", "bed", "beds", "floor", "wall", "walls",
    "minute", "power", "war", "force", "age", "care", "order", "case",

    # Common adjectives
    "good", "better", "best", "bad", "worse", "worst",
    "big", "bigger", "biggest", "small", "smaller", "smallest",
    "large", "larger", "largest", "little", "less", "least",
    "long", "longer", "longest", "short", "shorter", "shortest",
    "high", "higher", "highest", "low", "lower", "lowest",
    "old", "older", "oldest", "young", "younger", "youngest", "new", "newer", "newest",
    "great", "greater", "greatest", "important", "right", "left", "own",
    "other", "different", "same", "next", "last", "first", "second", "third",
    "early", "earlier", "earliest", "late", "later", "latest",
    "easy", "easier", "easiest", "hard", "harder", "hardest",
    "hot", "hotter", "hottest", "cold", "colder", "coldest",
    "warm", "warmer", "warmest", "cool", "cooler", "coolest",
    "fast", "faster", "fastest", "slow", "slower", "slowest",
    "strong", "stronger", "strongest", "weak", "weaker", "weakest",
    "happy", "happier", "happiest", "sad", "sadder", "saddest",
    "nice", "nicer", "nicest", "kind", "kinder", "kindest",
    "sure", "free", "full", "whole", "ready", "simple", "clear",
    "real", "true", "certain", "public", "able", "several",
    "open", "closed", "deep", "wide", "bright", "dark", "heavy", "light",
    "clean", "dirty", "wet", "dry", "soft", "hard", "quiet", "loud",
    "quick", "slow", "rich", "poor", "sick", "well", "dead", "alive",
    "empty", "busy", "pretty", "beautiful", "ugly",

    # Common adverbs
    "very", "too", "so", "more", "most", "less", "least",
    "well", "better", "best", "just", "only", "even", "still",
    "also", "just", "now", "then", "here", "there", "where",
    "how", "when", "why", "not", "never", "always", "often",
    "sometimes", "usually", "ever", "again", "back", "away",
    "together", "once", "twice", "soon", "today", "yesterday", "tomorrow",
    "already", "almost", "enough", "quite", "rather", "really",
    "perhaps", "maybe", "probably", "certainly", "surely",
    "yes", "no", "please", "thank", "sorry",

    # Numbers
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
    "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "million",
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",

    # Additional common words
    "able", "accept", "across", "act", "add", "afraid", "against", "agree",
    "allow", "alone", "appear", "apple", "area", "arm", "arrive", "art",
    "aunt", "ball", "become", "believe", "belong", "boat", "build",
    "burn", "business", "chair", "chance", "church", "clear", "climb",
    "clothe", "clothes", "company", "contain", "continue", "control",
    "cook", "corner", "cost", "count", "course", "cover", "create",
    "cross", "crowd", "cry", "decide", "depend", "describe", "develop",
    "die", "direction", "discover", "doctor", "double", "drop", "during",
    "edge", "effect", "eight", "either", "else", "enjoy", "enough",
    "enter", "example", "except", "excite", "expect", "explain", "express",
    "fact", "fair", "farm", "fear", "field", "fill", "final", "fine",
    "finger", "finish", "flower", "force", "foreign", "forest", "form",
    "fresh", "front", "garden", "general", "glass", "god", "gold",
    "hang", "hat", "hope", "hot", "idea", "include", "increase",
    "instead", "interest", "island", "join", "laugh", "law", "lead",
    "lie", "lift", "list", "lock", "love", "machine", "mark",
    "matter", "mean", "measure", "member", "mention", "middle", "mile",
    "mind", "miss", "moment", "nation", "natural", "nature", "necessary",
    "neighbor", "notice", "object", "ocean", "offer", "office", "opinion",
    "paint", "pair", "party", "pattern", "period", "pick", "plan",
    "plant", "position", "possible", "pound", "prepare", "present", "president",
    "press", "prince", "print", "probable", "produce", "promise", "proper",
    "protect", "prove", "purpose", "quarter", "queen", "question", "quick",
    "quiet", "race", "raise", "range", "rate", "reason", "receive",
    "record", "region", "remain", "reply", "report", "represent", "require",
    "rest", "result", "return", "roll", "rule", "sail", "salt",
    "save", "science", "season", "seat", "seem", "sell", "sense",
    "sentence", "separate", "serve", "set", "settle", "seven", "shape",
    "share", "ship", "shore", "sign", "silver", "single", "sir",
    "six", "size", "skin", "soldier", "solve", "south", "space",
    "special", "speed", "spell", "spend", "spread", "spring", "square",
    "step", "stone", "straight", "strange", "stream", "strength", "strike",
    "subject", "success", "sudden", "suffer", "suggest", "suit", "summer",
    "supply", "support", "suppose", "surface", "surprise", "sweet", "swim",
    "system", "tail", "taste", "teach", "team", "telephone", "television",
    "temperature", "ten", "test", "thick", "thin", "though", "thousand",
    "three", "tire", "total", "touch", "track", "train", "travel",
    "trip", "trouble", "type", "uncle", "understand", "unit", "universe",
    "value", "various", "view", "village", "visit", "voice", "vote",
    "wagon", "wander", "warm", "wash", "wave", "wealth", "weather",
    "weight", "welcome", "west", "wheel", "wild", "wind", "winter",
    "wish", "wonder", "wood", "yard", "yellow",
}


def compute_dale_chall(text: str) -> DaleChallResult:
    """
    Compute Dale-Chall Readability Formula.

    The Dale-Chall formula estimates reading difficulty based on the percentage
    of words that are NOT on a list of 3000 familiar words (words understood
    by 80% of 4th graders). It also considers average sentence length.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        Raw Score = 0.1579 * (difficult_words_pct) + 0.0496 * (avg_sentence_length)

        If difficult_words_pct > 5%:
            Adjusted Score = Raw Score + 3.6365

    Grade Level Correspondence:
        4.9 or lower: Grade 4 and below
        5.0-5.9: Grades 5-6
        6.0-6.9: Grades 7-8
        7.0-7.9: Grades 9-10
        8.0-8.9: Grades 11-12
        9.0-9.9: Grades 13-15 (College)
        10.0+: Grade 16+ (College Graduate)

    Advantages:
        - Based on empirical word familiarity data
        - Works well for educational materials
        - Well-validated across grade levels
        - Considers both vocabulary and syntax

    Disadvantages:
        - Requires maintaining 3000-word familiar list
        - List is dated (1948, updated 1995)
        - May not reflect modern vocabulary
        - Doesn't account for concept difficulty

    Args:
        text: Input text to analyze. Should contain at least one complete
              sentence. Empty text returns NaN values.

    Returns:
        DaleChallResult containing:
            - dale_chall_score: The Dale-Chall readability score
            - grade_level: Grade range (e.g., "7-8", "College")
            - difficult_word_count: Words not on familiar list
            - difficult_word_ratio: Difficult words / total words
            - avg_sentence_length: Average words per sentence
            - total_words: Total word count
            - metadata: List of difficult words, adjusted score flag, etc.

    Example:
        >>> result = compute_dale_chall("Sample educational text...")
        >>> print(f"Dale-Chall score: {result.dale_chall_score:.2f}")
        Dale-Chall score: 7.3
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 7-8
        >>> print(f"Difficult words: {result.difficult_word_ratio * 100:.1f}%")
        Difficult words: 12.4%

    Note:
        - Case-insensitive word matching
        - Punctuation stripped before word lookup
        - Proper nouns may be flagged as difficult even if well-known
        - Technical/specialized texts score higher than general texts
    """
    # Tokenize and segment
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return DaleChallResult(
            dale_chall_score=float("nan"),
            grade_level="Unknown",
            difficult_word_count=0,
            difficult_word_ratio=float("nan"),
            avg_sentence_length=float("nan"),
            total_words=0,
            metadata={
                "sentence_count": 0,
                "raw_score": float("nan"),
                "adjusted": False,
                "difficult_words_sample": [],
            },
        )

    # Count difficult words (not in familiar list)
    difficult_words = []
    for word in word_tokens:
        word_lower = word.lower()
        if word_lower not in DALE_CHALL_FAMILIAR_WORDS:
            difficult_words.append(word)

    difficult_word_count = len(difficult_words)
    difficult_word_ratio = difficult_word_count / len(word_tokens)
    difficult_word_pct = difficult_word_ratio * 100

    # Calculate average sentence length
    avg_sentence_length = len(word_tokens) / len(sentences)

    # Calculate raw score
    raw_score = 0.1579 * difficult_word_pct + 0.0496 * avg_sentence_length

    # Apply adjustment if difficult word % > 5.0
    adjusted = difficult_word_pct > 5.0
    if adjusted:
        dale_chall_score = raw_score + 3.6365
    else:
        dale_chall_score = raw_score

    # Map score to grade level
    if dale_chall_score < 5.0:
        grade_level = "4 and below"
    elif dale_chall_score < 6.0:
        grade_level = "5-6"
    elif dale_chall_score < 7.0:
        grade_level = "7-8"
    elif dale_chall_score < 8.0:
        grade_level = "9-10"
    elif dale_chall_score < 9.0:
        grade_level = "11-12"
    elif dale_chall_score < 10.0:
        grade_level = "College"
    else:
        grade_level = "College Graduate"

    # Build metadata
    # Sample up to 20 difficult words for metadata (avoid huge lists)
    difficult_words_sample = list(set(difficult_words))[:20]

    metadata = {
        "sentence_count": len(sentences),
        "raw_score": raw_score,
        "adjusted": adjusted,
        "difficult_word_pct": difficult_word_pct,
        "difficult_words_sample": difficult_words_sample,
        "familiar_word_list_size": len(DALE_CHALL_FAMILIAR_WORDS),
    }

    return DaleChallResult(
        dale_chall_score=dale_chall_score,
        grade_level=grade_level,
        difficult_word_count=difficult_word_count,
        difficult_word_ratio=difficult_word_ratio,
        avg_sentence_length=avg_sentence_length,
        total_words=len(word_tokens),
        metadata=metadata,
    )


def compute_linsear_write(text: str) -> LinsearWriteResult:
    """
    Compute Linsear Write Readability Formula.

    Developed for the U.S. Air Force to assess technical writing, the Linsear
    Write formula classifies words as "easy" (1-2 syllables) or "hard" (3+
    syllables) and uses sentence length to estimate grade level.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        1. Count "easy" words (1-2 syllables): multiply count by 1
        2. Count "hard" words (3+ syllables): multiply count by 3
        3. Divide sum by number of sentences
        4. If result > 20, divide by 2 to get grade level
        5. If result <= 20, subtract 2, then divide by 2

    The formula is optimized for technical writing and works best with
    passages of about 100 words.

    Advantages:
        - Simple binary classification (easy/hard)
        - Effective for technical documents
        - Fast computation
        - Developed specifically for instructional materials

    Disadvantages:
        - Less well-known than other formulas
        - Binary word classification is crude
        - May overestimate difficulty of technical terms
        - Limited validation compared to Flesch or Dale-Chall

    Args:
        text: Input text to analyze. Works best with 100-word samples.
              Empty text returns NaN values.

    Returns:
        LinsearWriteResult containing:
            - linsear_score: The Linsear Write score
            - grade_level: Corresponding U.S. grade level (integer)
            - easy_word_count: Words with 1-2 syllables
            - hard_word_count: Words with 3+ syllables
            - avg_sentence_length: Average words per sentence
            - metadata: Calculation details, sentence count, etc.

    Example:
        >>> result = compute_linsear_write("Technical manual text...")
        >>> print(f"Linsear Write score: {result.linsear_score:.2f}")
        Linsear Write score: 11.3
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 11
        >>> print(f"Easy words: {result.easy_word_count}")
        Easy words: 78
        >>> print(f"Hard words: {result.hard_word_count}")
        Hard words: 22

    Note:
        - Syllable counting required (use existing syllable module)
        - Punctuation and numbers typically excluded
        - Most accurate with 100-word samples
        - Grade level is rounded to nearest integer
    """
    # Tokenize and segment
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return LinsearWriteResult(
            linsear_score=float("nan"),
            grade_level=0,
            easy_word_count=0,
            hard_word_count=0,
            avg_sentence_length=float("nan"),
            metadata={"sentence_count": 0, "total_words": 0, "raw_score": float("nan")},
        )

    # Classify words as easy (1-2 syllables) or hard (3+ syllables)
    easy_word_count = 0
    hard_word_count = 0

    for word in word_tokens:
        syllable_count = count_syllables(word)
        if syllable_count <= 2:
            easy_word_count += 1
        else:
            hard_word_count += 1

    # Calculate weighted sum
    weighted_sum = (easy_word_count * 1) + (hard_word_count * 3)

    # Calculate score
    raw_score = weighted_sum / len(sentences)

    # Convert to grade level
    if raw_score > 20:
        grade_level = round(raw_score / 2)
    else:
        grade_level = round((raw_score - 2) / 2)

    # Ensure grade level is non-negative
    grade_level = max(0, grade_level)

    # Calculate average sentence length
    avg_sentence_length = len(word_tokens) / len(sentences)

    # Build metadata
    metadata = {
        "total_words": len(word_tokens),
        "sentence_count": len(sentences),
        "raw_score": raw_score,
        "weighted_sum": weighted_sum,
    }

    return LinsearWriteResult(
        linsear_score=raw_score,
        grade_level=grade_level,
        easy_word_count=easy_word_count,
        hard_word_count=hard_word_count,
        avg_sentence_length=avg_sentence_length,
        metadata=metadata,
    )


def compute_fry(text: str) -> FryResult:
    """
    Compute Fry Readability Graph metrics.

    The Fry Readability Graph plots average sentence length against average
    syllables per 100 words to determine reading difficulty. This implementation
    provides the numerical coordinates and estimated grade level.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Method:
        1. Select three 100-word samples from text
        2. Count average sentence length across samples
        3. Count average syllables per 100 words across samples
        4. Plot coordinates on Fry graph (or use numerical approximation)
        5. Determine grade level from graph zone

    The original Fry graph has zones corresponding to grade levels 1-17+.
    This implementation uses numerical approximation to estimate grade level.

    Advantages:
        - Visual/graphical approach (intuitive)
        - Uses two independent dimensions (length & syllables)
        - Well-validated for educational materials
        - Covers wide range of grade levels (1-17+)

    Disadvantages:
        - Requires exactly 100-word samples (padding/truncation needed)
        - Graph reading can be subjective
        - Less precise than formula-based methods
        - Multiple samples needed for reliability

    Args:
        text: Input text to analyze. Should contain at least 100 words.
              Shorter texts are padded or return limited results.

    Returns:
        FryResult containing:
            - avg_sentence_length: Average words per sentence
            - avg_syllables_per_100: Average syllables per 100 words
            - grade_level: Estimated grade level (e.g., "5", "7", "College")
            - graph_zone: Which zone of Fry graph (for validity checking)
            - metadata: Sample details, total sentences, syllables, etc.

    Example:
        >>> result = compute_fry("Educational text for grade assessment...")
        >>> print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
        Avg sentence length: 14.3
        >>> print(f"Syllables/100 words: {result.avg_syllables_per_100:.1f}")
        Syllables/100 words: 142.7
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 6

    Note:
        - Original method uses three 100-word samples
        - Implementation may use single sample or whole text
        - Syllable counting required
        - Grade level estimation uses zone boundaries
        - Some texts fall outside graph zones (marked as invalid)
    """
    # Tokenize and segment
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return FryResult(
            avg_sentence_length=float("nan"),
            avg_syllables_per_100=float("nan"),
            grade_level="Unknown",
            graph_zone="invalid",
            metadata={
                "total_sentences": 0,
                "total_syllables": 0,
                "total_words": 0,
                "sample_size": 0,
            },
        )

    # Use first 100 words for sample (or entire text if < 100 words)
    sample_size = min(100, len(word_tokens))
    sample_tokens = word_tokens[:sample_size]

    # Count syllables in sample
    total_syllables = sum(count_syllables(word) for word in sample_tokens)

    # Count sentences within the sample
    # We need to determine how many sentences are in the first sample_size words
    word_count_so_far = 0
    sentences_in_sample = 0
    for sent in sentences:
        sent_tokens = tokenize(sent)
        sent_word_tokens = normalize_for_readability(sent_tokens)
        if word_count_so_far + len(sent_word_tokens) <= sample_size:
            sentences_in_sample += 1
            word_count_so_far += len(sent_word_tokens)
        else:
            # Partial sentence in sample
            if word_count_so_far < sample_size:
                sentences_in_sample += 1
            break

    # Ensure at least 1 sentence for division
    sentences_in_sample = max(1, sentences_in_sample)

    # Calculate avg_sentence_length (for the sample)
    avg_sentence_length = sample_size / sentences_in_sample

    # Calculate avg_syllables_per_100 (scale if sample < 100)
    avg_syllables_per_100 = (total_syllables / sample_size) * 100

    # Map to grade level using Fry graph approximation
    # Fry graph zones (simplified numerical approximation):
    # These are rough boundaries based on Fry graph zones
    # X-axis: avg sentences per 100 words (inverse of avg_sentence_length)
    # Y-axis: avg syllables per 100 words

    # Determine grade level based on avg_sentence_length and avg_syllables_per_100
    # Higher syllables per 100 = higher grade
    # Longer sentences = higher grade
    # Simplified zone mapping:
    if avg_syllables_per_100 < 125:
        if avg_sentence_length < 7:
            grade_level = "1"
            graph_zone = "valid"
        elif avg_sentence_length < 11:
            grade_level = "2"
            graph_zone = "valid"
        else:
            grade_level = "3"
            graph_zone = "valid"
    elif avg_syllables_per_100 < 135:
        if avg_sentence_length < 8:
            grade_level = "2"
            graph_zone = "valid"
        elif avg_sentence_length < 12:
            grade_level = "3"
            graph_zone = "valid"
        else:
            grade_level = "4"
            graph_zone = "valid"
    elif avg_syllables_per_100 < 145:
        if avg_sentence_length < 9:
            grade_level = "3"
            graph_zone = "valid"
        elif avg_sentence_length < 13:
            grade_level = "5"
            graph_zone = "valid"
        else:
            grade_level = "6"
            graph_zone = "valid"
    elif avg_syllables_per_100 < 155:
        if avg_sentence_length < 10:
            grade_level = "4"
            graph_zone = "valid"
        elif avg_sentence_length < 14:
            grade_level = "7"
            graph_zone = "valid"
        else:
            grade_level = "8"
            graph_zone = "valid"
    elif avg_syllables_per_100 < 165:
        if avg_sentence_length < 12:
            grade_level = "6"
            graph_zone = "valid"
        elif avg_sentence_length < 16:
            grade_level = "9"
            graph_zone = "valid"
        else:
            grade_level = "10"
            graph_zone = "valid"
    elif avg_syllables_per_100 < 175:
        if avg_sentence_length < 14:
            grade_level = "8"
            graph_zone = "valid"
        elif avg_sentence_length < 18:
            grade_level = "11"
            graph_zone = "valid"
        else:
            grade_level = "12"
            graph_zone = "valid"
    else:  # avg_syllables_per_100 >= 175
        if avg_sentence_length < 16:
            grade_level = "10"
            graph_zone = "valid"
        elif avg_sentence_length < 20:
            grade_level = "College"
            graph_zone = "valid"
        else:
            grade_level = "College+"
            graph_zone = "valid"

    # Check if outside typical graph bounds
    if avg_syllables_per_100 > 185 or avg_sentence_length > 25:
        graph_zone = "above_graph"
    elif avg_syllables_per_100 < 110:
        graph_zone = "below_graph"

    # Build metadata
    metadata = {
        "total_sentences": len(sentences),
        "total_syllables": sum(count_syllables(w) for w in word_tokens),
        "total_words": len(word_tokens),
        "sample_size": sample_size,
        "sentences_in_sample": sentences_in_sample,
        "syllables_in_sample": total_syllables,
    }

    return FryResult(
        avg_sentence_length=avg_sentence_length,
        avg_syllables_per_100=avg_syllables_per_100,
        grade_level=grade_level,
        graph_zone=graph_zone,
        metadata=metadata,
    )


def compute_forcast(text: str) -> FORCASTResult:
    """
    Compute FORCAST Readability Formula.

    FORCAST (FORmula for CASTing readability) was developed by the U.S. military
    to assess readability without counting syllables. It uses only the count of
    single-syllable words as its metric, making it fast and simple.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        Grade Level = 20 - (N / 10)

        Where N is the number of single-syllable words in a 150-word sample.

    The formula is optimized for technical and military documents and works
    best with standardized 150-word samples.

    Advantages:
        - Extremely simple (only counts single-syllable words)
        - No sentence segmentation required
        - Fast computation
        - Developed specifically for military/technical texts

    Disadvantages:
        - Less well-known and validated than other formulas
        - Requires exactly 150-word samples
        - Single dimension (doesn't consider sentence length)
        - May not generalize well beyond military context

    Args:
        text: Input text to analyze. Works best with 150-word samples.
              Shorter texts are padded or scored proportionally.
              Longer texts use first 150 words or multiple samples.

    Returns:
        FORCASTResult containing:
            - forcast_score: The FORCAST readability score
            - grade_level: Corresponding U.S. grade level (integer)
            - single_syllable_ratio: Single-syllable words / total words
            - single_syllable_count: Count of single-syllable words
            - total_words: Total word count analyzed
            - metadata: Sample details, calculation specifics, etc.

    Example:
        >>> result = compute_forcast("Military technical document...")
        >>> print(f"FORCAST score: {result.forcast_score:.2f}")
        FORCAST score: 9.7
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 10
        >>> print(f"Single-syllable ratio: {result.single_syllable_ratio:.3f}")
        Single-syllable ratio: 0.687

    Note:
        - Syllable counting required (but only to identify 1-syllable words)
        - Recommended sample size is 150 words
        - Multiple samples can be averaged for longer texts
        - Simpler than most readability formulas
        - Grade levels typically range from 5-12
    """
    # Tokenize
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(word_tokens) == 0:
        return FORCASTResult(
            forcast_score=float("nan"),
            grade_level=0,
            single_syllable_ratio=float("nan"),
            single_syllable_count=0,
            total_words=0,
            metadata={"sample_size": 0, "scaled_n": float("nan")},
        )

    # Use first 150 words for sample (or entire text if < 150 words)
    sample_size = min(150, len(word_tokens))
    sample_tokens = word_tokens[:sample_size]

    # Count single-syllable words in sample
    single_syllable_count = 0
    for word in sample_tokens:
        if count_syllables(word) == 1:
            single_syllable_count += 1

    # Scale N to 150-word basis if sample < 150
    if sample_size < 150:
        scaled_n = single_syllable_count * (150 / sample_size)
    else:
        scaled_n = single_syllable_count

    # Calculate grade level: 20 - (N / 10)
    forcast_score = 20 - (scaled_n / 10)
    grade_level = round(forcast_score)

    # Ensure grade level is in reasonable range (0-20)
    grade_level = max(0, min(20, grade_level))

    # Calculate single syllable ratio (for the sample)
    single_syllable_ratio = single_syllable_count / sample_size

    # Build metadata
    metadata = {
        "sample_size": sample_size,
        "scaled_n": scaled_n,
        "total_words_in_text": len(word_tokens),
    }

    return FORCASTResult(
        forcast_score=forcast_score,
        grade_level=grade_level,
        single_syllable_ratio=single_syllable_ratio,
        single_syllable_count=single_syllable_count,
        total_words=sample_size,
        metadata=metadata,
    )


def compute_powers_sumner_kearl(text: str) -> PowersSumnerKearlResult:
    """
    Compute Powers-Sumner-Kearl Readability Formula.

    The Powers-Sumner-Kearl (PSK) formula is a recalibration of the Flesch
    Reading Ease formula, optimized for primary grade levels (grades 1-4).
    It uses the same inputs (sentence length, syllables per word) but with
    different coefficients.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        Grade Level = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029

    The formula was derived from analysis of primary-grade texts and provides
    more accurate grade-level estimates for beginning readers than the original
    Flesch formula.

    Advantages:
        - Optimized for primary grades (1-4)
        - More accurate than Flesch for young readers
        - Uses same inputs as Flesch (easy to compare)
        - Well-validated on educational materials

    Disadvantages:
        - Less accurate for higher grade levels
        - Less well-known than Flesch
        - Limited range (not suitable for college-level texts)
        - Requires syllable counting

    Args:
        text: Input text to analyze. Optimized for children's literature
              and primary-grade educational materials. Empty text returns
              NaN values.

    Returns:
        PowersSumnerKearlResult containing:
            - psk_score: The Powers-Sumner-Kearl score
            - grade_level: Corresponding grade (decimal, e.g., 2.5 = mid-2nd grade)
            - avg_sentence_length: Average words per sentence
            - avg_syllables_per_word: Average syllables per word
            - total_sentences: Total sentence count
            - total_words: Total word count
            - total_syllables: Total syllable count
            - metadata: Comparison to Flesch, calculation details, etc.

    Example:
        >>> result = compute_powers_sumner_kearl("Children's book text...")
        >>> print(f"PSK score: {result.psk_score:.2f}")
        PSK score: 2.3
        >>> print(f"Grade level: {result.grade_level:.1f}")
        Grade level: 2.3
        >>> print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
        Avg sentence length: 8.5

    Note:
        - Most accurate for grades 1-4
        - Can produce negative scores for very simple texts
        - Grade level is continuous (can be decimal)
        - Syllable counting required (same as Flesch)
        - Compare to Flesch results for validation
    """
    # Tokenize and segment
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return PowersSumnerKearlResult(
            psk_score=float("nan"),
            grade_level=float("nan"),
            avg_sentence_length=float("nan"),
            avg_syllables_per_word=float("nan"),
            total_sentences=0,
            total_words=0,
            total_syllables=0,
            metadata={
                "flesch_reading_ease": float("nan"),
                "flesch_kincaid_grade": float("nan"),
            },
        )

    # Count syllables
    total_syllables = sum(count_syllables(word) for word in word_tokens)

    # Calculate metrics
    avg_sentence_length = len(word_tokens) / len(sentences)
    avg_syllables_per_word = total_syllables / len(word_tokens)

    # Apply Powers-Sumner-Kearl formula
    # Grade = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029
    psk_score = (
        0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029
    )
    grade_level = round(psk_score, 1)  # Round to 1 decimal place

    # Optional: Calculate Flesch scores for comparison
    flesch_reading_ease = (
        206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    )
    flesch_kincaid_grade = (
        0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    )

    # Build metadata
    metadata = {
        "flesch_reading_ease": flesch_reading_ease,
        "flesch_kincaid_grade": flesch_kincaid_grade,
        "difference_from_flesch": psk_score - flesch_kincaid_grade,
        "words_per_sentence": avg_sentence_length,
        "syllables_per_word": avg_syllables_per_word,
    }

    return PowersSumnerKearlResult(
        psk_score=psk_score,
        grade_level=grade_level,
        avg_sentence_length=avg_sentence_length,
        avg_syllables_per_word=avg_syllables_per_word,
        total_sentences=len(sentences),
        total_words=len(word_tokens),
        total_syllables=total_syllables,
        metadata=metadata,
    )
