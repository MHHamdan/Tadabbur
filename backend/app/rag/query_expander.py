"""
Query expansion for Islamic terminology.

Expands queries with Arabic transliterations, synonyms, and related terms
to improve retrieval accuracy.

CAPS AND LIMITS:
- Max 5 expansion terms per query
- Intent-based expansion (story queries get prophet names, fiqh queries get rulings)
- Always preserves original query terms
"""
import re
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class QueryIntent(str, Enum):
    """Query intent categories."""
    VERSE_MEANING = "verse_meaning"
    STORY_EXPLORATION = "story_exploration"
    THEME_SEARCH = "theme_search"
    COMPARATIVE = "comparative"
    LINGUISTIC = "linguistic"
    RULING = "ruling"
    UNKNOWN = "unknown"


@dataclass
class ExpandedQuery:
    """Result of query expansion."""
    original: str
    expanded_terms: List[str]
    arabic_terms: List[str]
    combined: str
    expansion_applied: List[str]
    intent: QueryIntent


# Maximum expansions to add
MAX_EXPANSIONS = 5
MAX_ARABIC_TERMS = 3
MAX_COMBINED_LENGTH = 500  # Characters


# Islamic term mappings: English -> (Arabic, transliterations, synonyms, intents)
# intents: list of QueryIntent values this term is relevant to
ISLAMIC_TERM_MAPPINGS = {
    # Core concepts (all intents)
    "patience": ("صبر", ["sabr", "sabir", "sabireen"], ["steadfastness", "endurance"], None),
    "prayer": ("صلاة", ["salah", "salat"], ["worship"], None),
    "fasting": ("صوم", ["sawm", "siyam"], [], None),
    "charity": ("زكاة", ["zakah", "zakat", "sadaqah"], ["alms"], ["ruling"]),
    "pilgrimage": ("حج", ["hajj", "haj"], [], ["ruling"]),
    "faith": ("إيمان", ["iman", "imaan"], ["belief"], None),
    "trust": ("توكل", ["tawakkul"], ["reliance"], ["verse_meaning"]),
    "repentance": ("توبة", ["tawbah", "tawba"], ["seeking forgiveness"], None),
    "monotheism": ("توحيد", ["tawhid", "tawheed"], ["oneness of God"], None),
    "god-consciousness": ("تقوى", ["taqwa"], ["piety", "righteousness"], None),
    "gratitude": ("شكر", ["shukr"], ["thankfulness"], None),
    "remembrance": ("ذكر", ["dhikr", "zikr"], ["mention of Allah"], None),

    # Prophets (story_exploration intent)
    "adam": ("آدم", ["aadam"], ["first man"], ["story_exploration"]),
    "noah": ("نوح", ["nuh", "nooh"], ["prophet of the flood"], ["story_exploration"]),
    "abraham": ("إبراهيم", ["ibrahim", "ibraheem"], ["khalilullah"], ["story_exploration"]),
    "moses": ("موسى", ["musa", "moosa"], ["kalimullah"], ["story_exploration"]),
    "jesus": ("عيسى", ["isa", "eesa"], ["messiah"], ["story_exploration"]),
    "muhammad": ("محمد", ["mohammad", "mohammed"], ["prophet", "rasulullah"], ["story_exploration"]),
    "joseph": ("يوسف", ["yusuf", "yousuf"], [], ["story_exploration"]),
    "david": ("داود", ["dawud", "dawood"], [], ["story_exploration"]),
    "solomon": ("سليمان", ["sulayman", "sulaiman"], ["wise king"], ["story_exploration"]),
    "jonah": ("يونس", ["yunus", "younus"], [], ["story_exploration"]),
    "job": ("أيوب", ["ayyub", "ayub"], ["patient one"], ["story_exploration"]),
    "mary": ("مريم", ["maryam", "mariam"], ["mother of isa"], ["story_exploration"]),

    # Quranic terms (verse_meaning, theme_search)
    "verse": ("آية", ["ayah", "aya"], ["sign"], ["verse_meaning"]),
    "chapter": ("سورة", ["surah", "sura"], [], ["verse_meaning"]),
    "revelation": ("وحي", ["wahy", "wahi"], [], ["verse_meaning"]),
    "guidance": ("هداية", ["hidaya", "hidayah"], ["right path"], ["verse_meaning", "theme_search"]),
    "mercy": ("رحمة", ["rahma", "rahmah"], ["compassion"], ["verse_meaning", "theme_search"]),
    "punishment": ("عذاب", ["adhab", "azab"], ["torment"], ["verse_meaning"]),
    "paradise": ("جنة", ["jannah", "janna"], ["heaven"], ["theme_search"]),
    "hellfire": ("جهنم", ["jahannam"], ["hell"], ["theme_search"]),
    "angel": ("ملك", ["malak", "malaika"], [], ["verse_meaning"]),
    "jinn": ("جن", ["djinn"], ["unseen beings"], ["verse_meaning"]),
    "devil": ("شيطان", ["shaytan", "shaitan"], ["satan"], ["story_exploration"]),

    # Story-related (story_exploration)
    "story": ("قصة", ["qissa", "qissah"], ["narrative"], ["story_exploration"]),
    "pharaoh": ("فرعون", ["firawn", "firaun"], ["king of egypt"], ["story_exploration"]),
    "children of israel": ("بني إسرائيل", ["bani israel"], ["israelites"], ["story_exploration"]),
    "ark": ("سفينة", ["safinah"], ["ship"], ["story_exploration"]),
    "flood": ("طوفان", ["tufan"], ["deluge"], ["story_exploration"]),
    "cave": ("كهف", ["kahf"], [], ["story_exploration"]),

    # Fiqh/Rulings (ruling intent)
    "halal": ("حلال", ["halaal"], ["permissible"], ["ruling"]),
    "haram": ("حرام", ["haraam"], ["forbidden"], ["ruling"]),
    "obligatory": ("فرض", ["fard", "wajib"], [], ["ruling"]),
    "recommended": ("مستحب", ["mustahab", "sunnah"], [], ["ruling"]),
    "ruling": ("حكم", ["hukm"], ["decree"], ["ruling"]),
    "witness": ("شهادة", ["shahada", "shahadah"], [], ["ruling"]),

    # Linguistic (linguistic intent)
    "root": ("جذر", ["jadhr"], [], ["linguistic"]),
    "word": ("كلمة", ["kalima", "kalimah"], [], ["linguistic"]),
    "grammar": ("نحو", ["nahw"], [], ["linguistic"]),
    "meaning": ("معنى", ["maana", "ma'na"], [], ["linguistic", "verse_meaning"]),

    # Actions and concepts
    "worship": ("عبادة", ["ibadah", "ibadat"], ["devotion"], None),
    "sin": ("ذنب", ["dhanb", "zunub"], ["transgression"], None),
    "forgiveness": ("مغفرة", ["maghfirah"], ["pardon"], None),
    "test": ("ابتلاء", ["ibtila", "fitna"], ["trial"], None),
    "reward": ("أجر", ["ajr", "thawab"], ["recompense"], None),
}


class QueryExpander:
    """
    Expands queries with Islamic terminology to improve retrieval.

    Features:
    - Caps expansion to MAX_EXPANSIONS terms
    - Intent-based expansion (only adds relevant terms)
    - Preserves original query
    """

    def __init__(self):
        self.mappings = ISLAMIC_TERM_MAPPINGS
        self._build_reverse_index()

    def _build_reverse_index(self):
        """Build reverse index from all terms to canonical English."""
        self.reverse_index = {}

        for english, (arabic, translits, synonyms, intents) in self.mappings.items():
            # Map Arabic to English
            self.reverse_index[arabic] = english

            # Map transliterations to English
            for translit in translits:
                self.reverse_index[translit.lower()] = english

            # Map synonyms to English
            for synonym in synonyms:
                self.reverse_index[synonym.lower()] = english

            # Map English to itself
            self.reverse_index[english.lower()] = english

    def classify_intent(self, query: str) -> QueryIntent:
        """Classify query intent from query text."""
        q_lower = query.lower()

        if any(word in q_lower for word in ["meaning", "tafseer", "explain", "معنى", "تفسير"]):
            return QueryIntent.VERSE_MEANING

        if any(word in q_lower for word in ["story", "prophet", "قصة", "نبي"]):
            return QueryIntent.STORY_EXPLORATION

        if any(word in q_lower for word in ["theme", "topic", "about", "موضوع"]):
            return QueryIntent.THEME_SEARCH

        if any(word in q_lower for word in ["compare", "difference", "مقارنة", "فرق"]):
            return QueryIntent.COMPARATIVE

        if any(word in q_lower for word in ["root", "word", "grammar", "جذر", "كلمة"]):
            return QueryIntent.LINGUISTIC

        if any(word in q_lower for word in ["ruling", "halal", "haram", "allowed", "حكم", "حلال", "حرام"]):
            return QueryIntent.RULING

        return QueryIntent.VERSE_MEANING  # Default

    def _is_relevant_for_intent(self, term: str, intent: QueryIntent) -> bool:
        """Check if a term is relevant for the given intent."""
        if term not in self.mappings:
            return True  # Unknown terms are always relevant

        _, _, _, term_intents = self.mappings[term]

        # None means relevant to all intents
        if term_intents is None:
            return True

        return intent.value in term_intents

    def expand(self, query: str, intent: Optional[QueryIntent] = None) -> ExpandedQuery:
        """
        Expand a query with related Islamic terms.

        Args:
            query: Original user query
            intent: Optional intent (auto-classified if not provided)

        Returns:
            ExpandedQuery with capped expansion terms
        """
        original = query
        query_lower = query.lower()

        # Classify intent if not provided
        if intent is None:
            intent = self.classify_intent(query)

        # Extract words
        words = query_lower.split()

        expanded_terms = set()
        arabic_terms = set()
        expansions_applied = []

        # Check each word against mappings
        for word in words:
            # Clean word
            clean_word = re.sub(r'[^\w\u0600-\u06FF]', '', word)

            # Check if word is in reverse index
            if clean_word in self.reverse_index:
                canonical = self.reverse_index[clean_word]

                # Check if relevant for intent
                if not self._is_relevant_for_intent(canonical, intent):
                    continue

                if canonical in self.mappings:
                    arabic, translits, synonyms, _ = self.mappings[canonical]

                    # Add only the most relevant expansions
                    if len(expanded_terms) < MAX_EXPANSIONS:
                        expanded_terms.add(canonical)

                        # Add first transliteration only
                        if translits and len(expanded_terms) < MAX_EXPANSIONS:
                            expanded_terms.add(translits[0])

                        # Add first synonym only
                        if synonyms and len(expanded_terms) < MAX_EXPANSIONS:
                            expanded_terms.add(synonyms[0])

                    # Add Arabic term (limited)
                    if len(arabic_terms) < MAX_ARABIC_TERMS:
                        arabic_terms.add(arabic)

                    expansions_applied.append(f"{clean_word} -> {canonical}")

            # Check multi-word phrases
            for phrase, (arabic, translits, synonyms, term_intents) in self.mappings.items():
                if phrase in query_lower and len(phrase.split()) > 1:
                    # Check intent relevance
                    if term_intents is not None and intent.value not in term_intents:
                        continue

                    if len(expanded_terms) < MAX_EXPANSIONS:
                        expanded_terms.add(phrase)
                    if len(arabic_terms) < MAX_ARABIC_TERMS:
                        arabic_terms.add(arabic)
                    expansions_applied.append(f"{phrase} expanded")

        # Build combined query
        combined_parts = [original]

        # Add significant expanded terms (avoid duplicates)
        terms_added = 0
        for term in expanded_terms:
            if term.lower() not in query_lower and terms_added < MAX_EXPANSIONS:
                combined_parts.append(term)
                terms_added += 1

        # Add Arabic terms
        arabic_added = 0
        for arabic in arabic_terms:
            if arabic not in query and arabic_added < MAX_ARABIC_TERMS:
                combined_parts.append(arabic)
                arabic_added += 1

        combined = " ".join(combined_parts)

        # Enforce max length
        if len(combined) > MAX_COMBINED_LENGTH:
            combined = combined[:MAX_COMBINED_LENGTH].rsplit(' ', 1)[0]

        return ExpandedQuery(
            original=original,
            expanded_terms=list(expanded_terms)[:MAX_EXPANSIONS],
            arabic_terms=list(arabic_terms)[:MAX_ARABIC_TERMS],
            combined=combined,
            expansion_applied=expansions_applied,
            intent=intent,
        )

    def get_all_variants(self, term: str) -> Set[str]:
        """Get all variants of a term (Arabic, transliterations, synonyms)."""
        variants = set()
        term_lower = term.lower()

        # Check if term is a key
        if term_lower in self.mappings:
            arabic, translits, synonyms, _ = self.mappings[term_lower]
            variants.add(term_lower)
            variants.add(arabic)
            variants.update(t.lower() for t in translits)
            variants.update(s.lower() for s in synonyms)

        # Check reverse index
        elif term_lower in self.reverse_index:
            canonical = self.reverse_index[term_lower]
            return self.get_all_variants(canonical)

        return variants


# Global instance
query_expander = QueryExpander()


def expand_query(query: str, intent: Optional[QueryIntent] = None) -> ExpandedQuery:
    """Convenience function to expand a query."""
    return query_expander.expand(query, intent)


# Golden test cases for regression testing
GOLDEN_TESTS = [
    {
        "query": "What is the story of Moses?",
        "expected_intent": QueryIntent.STORY_EXPLORATION,
        "expected_terms": ["moses", "musa"],
        "max_expansions": MAX_EXPANSIONS,
    },
    {
        "query": "Is eating pork halal?",
        "expected_intent": QueryIntent.RULING,
        "expected_terms": ["halal"],
        "max_expansions": MAX_EXPANSIONS,
    },
    {
        "query": "Explain the meaning of sabr",
        "expected_intent": QueryIntent.VERSE_MEANING,
        "expected_terms": ["patience", "sabr"],
        "max_expansions": MAX_EXPANSIONS,
    },
    {
        "query": "What is the root of the word taqwa?",
        "expected_intent": QueryIntent.LINGUISTIC,
        "expected_terms": ["taqwa"],
        "max_expansions": MAX_EXPANSIONS,
    },
    {
        "query": "Theme of mercy in Quran",
        "expected_intent": QueryIntent.THEME_SEARCH,
        "expected_terms": ["mercy"],
        "max_expansions": MAX_EXPANSIONS,
    },
]


def run_golden_tests() -> list[dict]:
    """Run golden tests and return results."""
    results = []

    for test in GOLDEN_TESTS:
        query = test["query"]
        expected_intent = test["expected_intent"]
        expected_terms = test["expected_terms"]
        max_exp = test["max_expansions"]

        result = expand_query(query)

        # Check intent
        intent_match = result.intent == expected_intent

        # Check terms found
        all_terms = result.expanded_terms + result.arabic_terms + [result.original]
        all_terms_lower = [t.lower() for t in all_terms]
        terms_found = all(any(exp.lower() in t for t in all_terms_lower) for exp in expected_terms)

        # Check expansion cap
        under_cap = len(result.expanded_terms) <= max_exp

        results.append({
            "query": query,
            "intent_match": intent_match,
            "expected_intent": expected_intent.value,
            "actual_intent": result.intent.value,
            "terms_found": terms_found,
            "expected_terms": expected_terms,
            "actual_terms": result.expanded_terms,
            "under_cap": under_cap,
            "expansion_count": len(result.expanded_terms),
            "passed": intent_match and terms_found and under_cap,
        })

    return results
