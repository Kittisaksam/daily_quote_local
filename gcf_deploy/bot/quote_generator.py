"""Quote generation module using Claude API and local cache."""
import json
import random
from pathlib import Path
from typing import Optional
import anthropic
from config.settings import config


class QuoteGenerator:
    """Generate inspirational quotes from local cache or Claude AI."""

    def __init__(self, quotes_file: Optional[Path] = None, api_key: Optional[str] = None):
        """Initialize the quote generator.

        Args:
            quotes_file: Path to quotes JSON file
            api_key: Anthropic API key for Claude
        """
        self.quotes_file = quotes_file or config.quotes_file
        self.api_key = api_key or config.anthropic_api_key
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def get_local_quote(self, language: str = "both") -> dict:
        """Get a random quote from local cache.

        Args:
            language: Language preference ('en', 'th', or 'both')

        Returns:
            Dictionary with 'text', 'author', and 'language' keys
        """
        if not self.quotes_file.exists():
            return self._generate_ai_quote(language)

        with open(self.quotes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        quotes = data.get('quotes', [])

        # Filter by language if specified
        if language != "both":
            quotes = [q for q in quotes if q.get('language') == language]

        if not quotes:
            # No quotes found, generate one instead
            return self._generate_ai_quote(language)

        return random.choice(quotes)

    def _generate_ai_quote(self, language: str = "both") -> dict:
        """Generate a new inspirational quote using Claude AI.

        Args:
            language: Language preference ('en', 'th', or 'both')

        Returns:
            Dictionary with 'text', 'author', and 'language' keys
        """
        # Determine language for prompt
        if language == "both":
            # Randomly choose between English and Thai
            lang = random.choice(["en", "th"])
        else:
            lang = language

        if lang == "th":
            prompt = """สร้างคำคมเตือนใจที่สร้างแรงบันดาลใจ 1 ข้อ โดยมีลักษณะดังนี้:
- สั้น กระชับ และมีความหมายลึกซึ้ง
- เหมาะสำหรับแชร์ในโซเชียลมีเดีย
- ไม่ซ้ำซาก
- ไม่ต้องระบุผู้แต่ง (ใส่ "ไม่ระบุ")

ตอบเป็น JSON เท่านั้น:
{
  "text": "คำคมที่สร้างขึ้น",
  "author": "ไม่ระบุ",
  "language": "th"
}"""
        else:
            prompt = """Generate 1 original, inspirational quote with these characteristics:
- Short, concise, and meaningful
- Suitable for social media sharing
- Unique and not cliché
- Author can be "Unknown" if not applicable

Respond ONLY with valid JSON:
{
  "text": "the quote text",
  "author": "author name",
  "language": "en"
}"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.8,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            content = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                # Extract content between ``` markers
                parts = content.split("```")
                if len(parts) >= 2:
                    content = parts[1].strip()
                    # Remove language identifier if present (e.g., "json", "python")
                    if content.startswith(("json", "python", "text")):
                        content = content.split("\n", 1)[1].strip() if "\n" in content else content.strip()

            # Try to parse as JSON
            try:
                quote_data = json.loads(content)
                # Ensure it has the required fields
                if 'text' not in quote_data:
                    quote_data['text'] = content
                if 'author' not in quote_data:
                    quote_data['author'] = 'Claude AI'
                if 'language' not in quote_data:
                    quote_data['language'] = lang
                return quote_data
            except json.JSONDecodeError:
                # If not JSON, return the text as quote
                return {
                    'text': content,
                    'author': 'Claude AI',
                    'language': lang
                }

        except Exception as e:
            print(f"Error generating AI quote: {e}")
            # Fallback to a simple quote
            if lang == "th":
                return {
                    'text': 'ทุกวันเป็นโอกาสใหม่ในการเริ่มต้นใหม่',
                    'author': 'ไม่ระบุ',
                    'language': 'th'
                }
            else:
                return {
                    'text': 'Every day is a new opportunity to start fresh.',
                    'author': 'Unknown',
                    'language': 'en'
                }

    def get_quote(self, prefer_ai: bool = False, language: str = "both") -> dict:
        """Get a quote from local cache or AI generation.

        Args:
            prefer_ai: If True, prefer AI-generated quotes
            language: Language preference ('en', 'th', or 'both')

        Returns:
            Dictionary with 'text', 'author', and 'language' keys
        """
        if prefer_ai or random.random() < 0.3:  # 30% chance of AI quote by default
            quote = self._generate_ai_quote(language)
            quote['source'] = 'ai'
        else:
            quote = self.get_local_quote(language)
            quote['source'] = 'local'

        return quote

    def add_quote_to_cache(self, text: str, author: str = "Unknown", language: str = "en"):
        """Add a new quote to the local cache.

        Args:
            text: Quote text
            author: Quote author
            language: Quote language ('en' or 'th')
        """
        # Load existing quotes
        if self.quotes_file.exists():
            with open(self.quotes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {'quotes': []}

        # Add new quote
        new_quote = {
            'text': text,
            'author': author,
            'language': language
        }
        data['quotes'].append(new_quote)

        # Save back to file
        with open(self.quotes_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# Singleton instance
_generator = None


def get_quote_generator() -> QuoteGenerator:
    """Get the singleton quote generator instance."""
    global _generator
    if _generator is None:
        _generator = QuoteGenerator()
    return _generator


def get_quote(prefer_ai: bool = False, language: str = "both") -> dict:
    """Convenience function to get a quote.

    Args:
        prefer_ai: If True, prefer AI-generated quotes
        language: Language preference ('en', 'th', or 'both')

    Returns:
        Dictionary with 'text', 'author', and 'language' keys
    """
    generator = get_quote_generator()
    return generator.get_quote(prefer_ai=prefer_ai, language=language)
