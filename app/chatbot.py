from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9]+")
CONTACT_SOURCE = {
    "title": "Contact SafeX",
    "url": "https://safexsolutions.com/contact/",
    "category": "Contact",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "has",
    "have",
    "help",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "safe",
    "safex",
    "that",
    "the",
    "their",
    "to",
    "we",
    "what",
    "with",
    "you",
    "your",
}
SMALL_TALK_RESPONSES = {
    "greeting": (
        "Hello! I am the SafeX AI Assistant. You can ask me about SafeX services, "
        "AI chatbots, cybersecurity, web development, digital marketing, creative media, "
        "or training programs."
    ),
    "wellbeing": (
        "I am doing great, thanks for asking. I am ready to help you explore SafeX "
        "services or answer quick questions about this prototype."
    ),
    "thanks": "You are welcome. Ask me anything about SafeX whenever you are ready.",
    "goodbye": "Goodbye! Feel free to come back if you need more information about SafeX.",
}


@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    title: str
    category: str
    content: str
    source: str
    sample_questions: tuple[str, ...]


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_RE.findall(text.lower())
        if len(token) > 1 and token not in STOPWORDS
    ]


def _entry_text(entry: KnowledgeEntry) -> str:
    questions = " ".join(entry.sample_questions)
    return f"{entry.title} {entry.category} {entry.content} {questions}"


def _small_talk_intent(text: str) -> str | None:
    normalized = " ".join(TOKEN_RE.findall(text.lower()))
    tokens = set(normalized.split())

    greeting_phrases = {"hi", "hello", "hey", "salam", "assalamualaikum"}
    if normalized in greeting_phrases or tokens & greeting_phrases:
        return "greeting"

    if (
        "how are you" in normalized
        or "how r you" in normalized
        or "how you doing" in normalized
        or {"how", "are", "you"}.issubset(tokens)
    ):
        return "wellbeing"

    if tokens & {"thanks", "thankyou"} or "thank you" in normalized:
        return "thanks"

    if tokens & {"bye", "goodbye"} or "see you" in normalized:
        return "goodbye"

    return None


class SafeXFAQBot:
    """Small TF-IDF FAQ assistant over curated SafeX public website content."""

    def __init__(self, knowledge_path: Path) -> None:
        raw_entries = json.loads(knowledge_path.read_text(encoding="utf-8"))
        self.entries = [
            KnowledgeEntry(
                id=item["id"],
                title=item["title"],
                category=item["category"],
                content=item["content"],
                source=item["source"],
                sample_questions=tuple(item.get("sample_questions", [])),
            )
            for item in raw_entries
        ]
        self._document_tokens = [_tokenize(_entry_text(entry)) for entry in self.entries]
        self._idf = self._build_idf(self._document_tokens)
        self._vectors = [self._vectorize(tokens) for tokens in self._document_tokens]

    @staticmethod
    def _build_idf(documents: list[list[str]]) -> dict[str, float]:
        document_count = len(documents)
        document_frequency: Counter[str] = Counter()
        for tokens in documents:
            document_frequency.update(set(tokens))
        return {
            token: math.log((document_count + 1) / (frequency + 1)) + 1
            for token, frequency in document_frequency.items()
        }

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        counts = Counter(tokens)
        total = sum(counts.values())
        return {
            token: (count / total) * self._idf.get(token, 0.0)
            for token, count in counts.items()
        }

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(weight * right.get(token, 0.0) for token, weight in left.items())
        left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
        right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    def answer(self, message: str) -> dict[str, Any]:
        cleaned = message.strip()
        if not cleaned:
            return {
                "answer": "Ask me about SafeX services, training programs, AI automation, cybersecurity, web development, or digital marketing.",
                "confidence": 0.0,
                "sources": [],
                "suggested_questions": self.suggested_questions(),
            }

        small_talk_intent = _small_talk_intent(cleaned)
        if small_talk_intent is not None:
            return {
                "answer": SMALL_TALK_RESPONSES[small_talk_intent],
                "confidence": 1.0,
                "sources": [],
                "suggested_questions": self.suggested_questions(),
            }

        query_tokens = _tokenize(cleaned)
        query_vector = self._vectorize(query_tokens)
        scored_entries = [
            (self._cosine(query_vector, document_vector), entry)
            for document_vector, entry in zip(self._vectors, self.entries)
        ]
        scored_entries.sort(key=lambda item: item[0], reverse=True)
        best_score, best_entry = scored_entries[0]

        if best_score < 0.06:
            return {
                "answer": (
                    "I do not have enough information about that in my current SafeX knowledge base. "
                    "For the most accurate answer, please contact the SafeX team through the official "
                    "website contact page."
                ),
                "confidence": round(best_score, 3),
                "sources": [CONTACT_SOURCE],
                "suggested_questions": self.suggested_questions(),
            }

        related = [
            entry
            for score, entry in scored_entries[1:3]
            if score >= max(0.05, best_score * 0.72)
        ]
        entries = [best_entry, *related]
        answer_parts = [entry.content for entry in entries]
        sources = [
            {"title": entry.title, "url": entry.source, "category": entry.category}
            for entry in entries
        ]
        return {
            "answer": " ".join(answer_parts),
            "confidence": round(best_score, 3),
            "sources": sources,
            "suggested_questions": self.suggested_questions(best_entry.category),
        }

    def suggested_questions(self, category: str | None = None) -> list[str]:
        preferred = [
            question
            for entry in self.entries
            if category is None or entry.category == category
            for question in entry.sample_questions[:2]
        ]
        fallback = [
            "What services does SafeX offer?",
            "Can SafeX build an AI chatbot?",
            "Does SafeX provide cybersecurity services?",
            "What is the SafeX Digital Community?",
        ]
        combined = [*preferred, *fallback]
        unique: list[str] = []
        for question in combined:
            if question not in unique:
                unique.append(question)
            if len(unique) == 4:
                break
        return unique


@lru_cache(maxsize=1)
def get_bot() -> SafeXFAQBot:
    root = Path(__file__).resolve().parents[1]
    return SafeXFAQBot(root / "data" / "safex_knowledge.json")
