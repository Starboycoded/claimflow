"""
Message intake — handles WhatsApp, web form, and API submissions.
Normalizes all input sources into a standard claim format.
"""
import re
from datetime import datetime

class IntakeReceiver:
    """Receive and validate incoming claims from any channel."""

    SUPPORTED_SOURCES = ["whatsapp", "web", "api", "email"]
    MAX_TEXT_LENGTH = 5000
    MAX_IMAGES = 5

    def process(self, message: dict) -> dict:
        """
        Normalize and validate an incoming claim message.
        Returns validated intake or rejection.
        """
        source = message.get("source", "api")
        if source not in self.SUPPORTED_SOURCES:
            return {"rejected": True, "reason": f"Unsupported source: {source}"}

        text = message.get("text", "").strip()
        images = message.get("images", [])[:self.MAX_IMAGES]

        if not text and not images:
            return {"rejected": True, "reason": "No text or images provided"}

        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[:self.MAX_TEXT_LENGTH] + "..."

        clean_text = self._clean_text(text)
        language = self._detect_language(clean_text)

        return {
            "rejected": False,
            "clean_text": clean_text,
            "original_text": text,
            "image_count": len(images),
            "source": source,
            "language": language,
            "received_at": datetime.now().isoformat(),
            "has_images": len(images) > 0,
            "word_count": len(clean_text.split())
        }

    def _clean_text(self, text: str) -> str:
        """Remove noise, normalize whitespace."""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character sets."""
        if not text:
            return "en"
        if any('\u0600' <= c <= '\u06ff' for c in text):
            return "ar"
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return "zh"
        if any(w in text.lower().split() for w in ['le','la','les','est','que','dans','pour']):
            return "fr"
        if any(w in text.lower().split() for w in ['el','la','los','que','por','para','como']):
            return "es"
        return "en"
