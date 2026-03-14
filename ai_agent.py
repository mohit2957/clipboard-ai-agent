"""
═══════════════════════════════════════
  AI Agent
  Uses Ollama llama3:8b for content
  classification and smart search
═══════════════════════════════════════
"""

import re
import json
import ollama
from config import MODEL_NAME, MAX_CONTENT_LENGTH


class AIAgent:
    def __init__(self):
        """Initialize the AI agent with the configured model."""
        self.model = MODEL_NAME
        print(f"[AI Agent] Using model: {self.model}")

    # ═══════════════════════════════════════
    #  CONTENT ANALYSIS
    # ═══════════════════════════════════════

    def analyze_content(self, content, content_type):
        """
        Send clipboard content to LLM for analysis.

        Returns:
            tuple: (category, summary, tags)
        """
        try:
            prompt = self._build_analysis_prompt(content, content_type)

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'You are a content classifier. '
                            'Respond with ONLY valid JSON. '
                            'No markdown fences. No explanation.'
                        )
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            result_text = response['message']['content'].strip()
            return self._parse_analysis_response(result_text, content)

        except Exception as e:
            print(f"[AI Agent Error] Analysis failed: {e}")
            return self._fallback_analysis(content)

    def _build_analysis_prompt(self, content, content_type):
        """Build the prompt for content analysis."""
        truncated = content[:MAX_CONTENT_LENGTH]

        return f"""Analyze this clipboard content and return a JSON object with exactly these 3 fields:

- "category": one short category label
  Examples: "Code", "Email", "URL", "Note", "Address",
  "Password", "Social Media", "Documentation", "News",
  "Shopping", "Recipe", "General"

- "summary": one sentence summary, max 15 words

- "tags": comma-separated relevant tags, max 5 tags

Content type: {content_type}
Content:
\"\"\"
{truncated}
\"\"\"

Return ONLY valid JSON. No explanation. No markdown."""

    def _parse_analysis_response(self, result_text, original_content):
        """Parse the JSON response from the LLM."""
        # Find JSON object in response
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)

        if json_match:
            result = json.loads(json_match.group())
            category = result.get('category', 'General')
            summary = result.get('summary', original_content[:50])
            tags = result.get('tags', '')

            print(f"[AI Agent] Category: {category} | Tags: {tags}")
            return (category, summary, tags)

        print("[AI Agent] Could not parse JSON, using fallback.")
        return self._fallback_analysis(original_content)

    def _fallback_analysis(self, content):
        """Fallback when LLM fails."""
        if isinstance(content, str):
            preview = content[:50].replace('\n', ' ')
        else:
            preview = 'Image'
        return ('General', preview, '')

    # ═══════════════════════════════════════
    #  SMART SEARCH
    # ═══════════════════════════════════════

    def smart_search(self, query, items):
        """
        Use LLM to find semantically matching items.

        Args:
            query: User's search query
            items: List of database rows

        Returns:
            list: Matching item IDs
        """
        try:
            items_text = self._format_items_for_search(items)

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'You are a search assistant. '
                            'Return ONLY comma-separated numeric IDs '
                            'that match the search query. '
                            'Nothing else. No explanation.'
                        )
                    },
                    {
                        'role': 'user',
                        'content': f"Search query: '{query}'\n\nItems:\n{items_text}"
                    }
                ]
            )

            response_text = response['message']['content']
            ids = re.findall(r'\d+', response_text)
            matching_ids = [int(i) for i in ids]

            print(f"[AI Agent] Smart search found IDs: {matching_ids}")
            return matching_ids

        except Exception as e:
            print(f"[AI Agent Error] Smart search failed: {e}")
            return []

    def _format_items_for_search(self, items, max_items=20):
        """Format database items as text for LLM search."""
        lines = []
        for item in items[:max_items]:
            item_id = item[0]
            item_type = item[1]
            content_preview = item[2][:80].replace('\n', ' ')
            category = item[3]
            tags = item[5]
            lines.append(
                f"ID:{item_id} | Type:{item_type} | "
                f"Category:{category} | Tags:{tags} | "
                f"Content:{content_preview}"
            )
        return "\n".join(lines)