"""Expression analysis metrics for stylometric fingerprinting.

This subpackage analyzes expressive elements in text — abbreviations,
emoticons, emoji, and other non-standard linguistic features — that serve
as reliable authorship markers. These features are especially powerful in
informal writing contexts (social media, forums, messaging) where authors
develop distinctive, habitual patterns.

Related GitHub Issues:
    #30 - Whonix stylometric features
    https://github.com/craigtrim/pystylometry/issues/30

Whonix Source:
    The Whonix Stylometry documentation identifies abbreviations, emoticons,
    and expressive elements as key deanonymization vectors.
    https://www.whonix.org/wiki/Stylometry

Modules:
    abbreviations: Contraction, acronym, and shorthand pattern analysis
    emoticons: Emoji, text emoticon, and expressive punctuation analysis
"""

from .abbreviations import compute_abbreviations
from .emoticons import compute_emoticons

__all__ = [
    "compute_abbreviations",
    "compute_emoticons",
]
