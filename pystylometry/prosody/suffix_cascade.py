"""Suffix-stripping CMU fallback for OOV stress recovery.

When ``phones_for_word()`` finds no CMU dictionary entry for a word, this
module attempts to recover its stress pattern by:

    1. Querying the lookup libraries (BNC, WordNet, optionally Google Ngrams)
       for the word's derivational suffixes.
    2. Recursively stripping suffixes (outermost-first) from the surface form,
       applying allomorphic restoration at each step.
    3. Trying the resulting stem in CMU at each level of stripping.
    4. If a CMU-lookable stem is found, reconstructing a synthetic ARPAbet
       phoneme string by appending unstressed placeholder syllables for the
       stripped suffix material.

The lookup libraries ship with pre-computed suffix data built offline by the
`morphroot <https://github.com/craigtrim/morphroot>`_ compiler.  **morphroot
is not needed at runtime** — the suffix data is baked into static hash-bucketed
modules inside each lookup package.

Related GitHub Issues:
    #82 — Suffix-stripping CMU fallback via lookup libraries for OOV stress
           recovery
           https://github.com/craigtrim/pystylometry/issues/82
    #81 — G2P cascade design (this implements Tier 2)
           https://github.com/craigtrim/pystylometry/issues/81
    #76 — Beat detection (primary downstream consumer)
           https://github.com/craigtrim/pystylometry/issues/76

Linguistic Background:
    Most English derivational suffixes are **stress-neutral** — they attach
    without altering the stress pattern of the base.  This was formalized by
    Chomsky & Halle (1968) and refined in lexical phonology (Kiparsky 1982,
    Mohanan 1986).

    Stress-neutral suffixes include the most productive English derivational
    morphemes: ``-ness``, ``-less``, ``-ful``, ``-ly``, ``-ment``, ``-er``
    (agentive), ``-ing``, ``-ed``.  For these, the root's CMU stress pattern
    is a reliable proxy for the derived form, with unstressed syllables
    appended for the suffix material.

    Stress-shifting suffixes (``-tion``, ``-ity``, ``-ic``) move primary
    stress to a predictable position relative to the suffix.  This module
    handles them conservatively — returning the root pattern with unstressed
    suffix syllables rather than attempting stress reassignment.

References:
    Chomsky, N. & Halle, M. (1968). *The Sound Pattern of English*.
        Harper & Row.
    Kiparsky, P. (1982). Lexical morphology and phonology. In I. S. Yang
        (Ed.), *Linguistics in the Morning Calm*, 3-91. Hanshin.
    Mohanan, K. P. (1986). *The Theory of Lexical Phonology*. Reidel.
    Weide, R. L. (1998). The CMU Pronouncing Dictionary, release 0.6d.
        Carnegie Mellon University.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Suffix syllable counts — how many syllable nuclei each suffix contributes.
# Used when reconstructing an ARPAbet string from a root's CMU entry.
#
# Values are conservative (based on standard pronunciation).  Suffixes not
# in this table default to 1 syllable.
# ---------------------------------------------------------------------------

_SUFFIX_SYLLABLES: dict[str, int] = {
    # Stress-neutral — no shift, append unstressed syllable(s)
    "ness": 1,
    "less": 1,
    "ful": 1,
    "ment": 1,
    "ship": 1,
    "ly": 1,
    "er": 1,
    "or": 1,
    "ist": 1,
    "ism": 2,
    "ward": 1,
    "wards": 1,
    "wise": 1,
    "dom": 1,
    "hood": 1,
    "like": 1,
    "ish": 1,
    "en": 1,
    "ern": 1,
    # Inflectional — variable syllable contribution
    "ing": 1,
    "ed": 0,  # Usually does not add a syllable (walked, jumped)
    "s": 0,
    "es": 0,
    "est": 1,
    # Stress-shifting — treated conservatively as unstressed
    "tion": 1,
    "sion": 1,
    "ation": 2,
    "ity": 2,
    "ic": 1,
    "ical": 2,
    "ous": 1,
    "al": 1,
    "ive": 1,
    "ent": 1,
    "ence": 1,
    "ance": 1,
    "able": 2,
    "ible": 2,
    "ize": 1,
    "ise": 1,
    "ery": 2,
}


def _restore_stem(surface: str, suffix: str) -> str:
    """Apply allomorphic restoration to recover the underlying stem.

    English derivational morphology frequently alters the surface form of the
    base when a suffix attaches.  These alternations are regular and reversible:

    - **Consonant doubling** before ``-ing``/``-ed``:
      ``running`` → strip ``-ing`` → ``runn`` → restore → ``run``
    - **Y → I lowering** before ``-ness``/``-ly``/``-ful`` etc.:
      ``happiness`` → strip ``-ness`` → ``happi`` → restore → ``happy``
    - **E-elision** before vowel-initial suffixes:
      ``hoping`` → strip ``-ing`` → ``hop`` (e-restore handled at lookup)

    Args:
        surface: The raw stem after mechanically stripping the suffix.
        suffix: The suffix that was stripped (determines which rules apply).

    Returns:
        The restored stem form, suitable for CMU dictionary lookup.
    """
    stem = surface

    # Consonant doubling: runn -> run, swimm -> swim
    if suffix in ("ing", "ed", "er", "est"):
        if (
            len(stem) >= 2
            and stem[-1] == stem[-2]
            and stem[-1] not in "aeiou"
        ):
            stem = stem[:-1]

    # Y → I restoration: happi -> happy, easi -> easy
    if suffix in ("ness", "less", "ly", "ful", "ment", "er", "est", "ish",
                   "ed", "es"):
        if stem.endswith("i"):
            stem = stem[:-1] + "y"

    return stem


def _try_cmu(
    stem: str,
    cmu_dict: dict[str, list[list[str]]],
) -> Optional[str]:
    """Try looking up *stem* in CMU, including British→American spelling variants.

    CMU is an American English dictionary.  Many BNC-sourced OOV words are
    British spellings that differ only in predictable ways:

    - ``-our`` → ``-or`` (colour → color)
    - ``-ise`` → ``-ize`` (organise → organize)
    - ``-re``  → ``-er`` (centre → center)

    Args:
        stem: Candidate stem to look up.
        cmu_dict: The loaded CMU dictionary (word → list of pronunciations).

    Returns:
        The exact key that matched in CMU, or None if no match.
    """
    if stem in cmu_dict:
        return stem

    # British → American spelling normalization
    if stem.endswith("our"):
        us = stem[:-3] + "or"
        if us in cmu_dict:
            return us

    if stem.endswith("ise"):
        us = stem[:-3] + "ize"
        if us in cmu_dict:
            return us

    if stem.endswith("re") and not stem.endswith("ure"):
        us = stem[:-2] + "er"
        if us in cmu_dict:
            return us

    return None


def _get_suffixes(word: str) -> Optional[list[str]]:
    """Query available lookup libraries for the word's derivational suffixes.

    Tries BNC first (broadest coverage of formal/academic register), then
    WordNet (curated, smaller), then Google Ngrams (if suffix data is
    installed).  Returns the first non-None result.

    All three libraries expose the same API:

    - ``get_suffixes(word) → list[str]``: suffixes in innermost-first order
    - Returns ``None`` if the word is not in that corpus
    - Returns ``[]`` if the word is in the corpus but monomorphemic

    Args:
        word: Lowercase word to look up.

    Returns:
        List of suffixes in innermost-first order (e.g. ``["ful", "ly"]``
        for "beautifully"), empty list if monomorphemic, or None if no
        library can identify the word.

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """
    # BNC — British National Corpus, ~669K entries
    try:
        from bnc_lookup import get_suffixes as bnc_suffixes  # type: ignore[import-untyped]

        result = bnc_suffixes(word)
        if result is not None:
            return result
    except (ImportError, Exception):
        pass

    # WordNet — ~88K entries, curated
    try:
        from wordnet_lookup import get_suffixes as wn_suffixes  # type: ignore[import-untyped]

        result = wn_suffixes(word)
        if result is not None:
            return result
    except (ImportError, Exception):
        pass

    # Google Ngrams — ~5M entries (requires suffix parquet to be installed)
    try:
        from gngram_lookup import get_suffixes as gn_suffixes  # type: ignore[import-untyped]

        result = gn_suffixes(word)
        if result is not None:
            return result
    except (ImportError, Exception):
        pass

    return None


def _build_synthetic_phones(
    root_phones: str,
    suffix_syllables: int,
) -> str:
    """Construct a synthetic ARPAbet string by appending unstressed syllables.

    The root's CMU phoneme string provides the authentic stress pattern for
    the base word.  For each suffix syllable, we append a placeholder
    unstressed vowel (``AH0``) to extend the pattern.  The consonant
    phonemes are placeholders — only the stress digits matter for downstream
    prosodic analysis (``_get_stress_pattern``, ``syllable_count``).

    Args:
        root_phones: Space-joined ARPAbet string from CMU for the root.
        suffix_syllables: Number of syllable nuclei the suffix contributes.

    Returns:
        Extended ARPAbet string with the suffix syllables appended.

    Example::

        >>> _build_synthetic_phones("HH AE1 P IY0", 1)  # happy + -ness
        'HH AE1 P IY0 N AH0'
    """
    if suffix_syllables <= 0:
        return root_phones

    # Append placeholder unstressed syllables (AH0 is the most common
    # English unstressed vowel — schwa).  A consonant onset (N) is
    # included for phonotactic plausibility, though it doesn't affect
    # stress extraction.
    suffix_phonemes = " ".join("N AH0" for _ in range(suffix_syllables))
    return f"{root_phones} {suffix_phonemes}"


def suffix_cascade_lookup(
    word: str,
    cmu_dict: dict[str, list[list[str]]],
) -> Tuple[List[str], str]:
    """Attempt to recover pronunciation for an OOV word via suffix stripping.

    This is the main entry point for the suffix cascade.  It is called by
    ``phones_for_word()`` when the direct CMU lookup returns no results.

    Algorithm:
        1. Query lookup libraries for the word's suffix decomposition.
        2. Strip suffixes outermost-first from the surface form, applying
           allomorphic restoration at each level.
        3. At each level, try the resulting stem in CMU (with British→American
           normalization).
        4. If a CMU hit is found, reconstruct a synthetic ARPAbet string by
           appending unstressed placeholder syllables for the stripped suffix
           material.

    Args:
        word: The OOV word (lowercase).
        cmu_dict: The loaded CMU dictionary.

    Returns:
        A 2-tuple of ``(phones_list, source)``:

        - ``phones_list``: A list of space-joined ARPAbet strings (same
          format as ``phones_for_word``).  Empty list if recovery failed.
        - ``source``: ``"suffix_cascade"`` if recovery succeeded,
          ``""`` if it failed.

    Related GitHub Issues:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
        #81 — G2P cascade design (Tier 2)
              https://github.com/craigtrim/pystylometry/issues/81

    Example::

        >>> phones, source = suffix_cascade_lookup("happiness", cmu_dict)
        >>> phones
        ['HH AE1 P IY0 N AH0']
        >>> source
        'suffix_cascade'
    """
    suffixes = _get_suffixes(word)
    if not suffixes:
        return [], ""

    # Strip suffixes outermost-first (the list is innermost-first, so reverse)
    current = word
    total_suffix_syllables = 0
    stripped: list[str] = []

    for suffix in reversed(suffixes):
        # Direct match: surface form ends with the suffix
        if current.endswith(suffix):
            raw = current[: -len(suffix)]
        # E-restore: the trailing 'e' was elided before a vowel-initial suffix
        # e.g., criticised -> criticis + e-restore -> criticise -> strip -ise
        elif (current + "e").endswith(suffix):
            raw = (current + "e")[: -len(suffix)]
        else:
            # Suffix doesn't match the current surface — skip
            continue

        current = _restore_stem(raw, suffix)
        stripped.append(suffix)
        total_suffix_syllables += _SUFFIX_SYLLABLES.get(suffix, 1)

        # Try the stem in CMU
        hit = _try_cmu(current, cmu_dict)
        if hit:
            # Found a CMU-lookable ancestor — reconstruct phonemes
            root_entries = cmu_dict[hit]
            # Use the first (most common) pronunciation
            root_phones = " ".join(root_entries[0])

            synthetic = _build_synthetic_phones(root_phones, total_suffix_syllables)
            return [synthetic], "suffix_cascade"

    return [], ""
