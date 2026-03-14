"""
═══════════════════════════════════════
  Content Detector
  Identifies clipboard content type:
  text, link, or image
═══════════════════════════════════════
"""

import re


class ContentDetector:
    """Detects whether clipboard text is a URL/link or plain text."""

    # Regex pattern for URLs
    URL_PATTERN = re.compile(
        r'^(https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)$',
        re.IGNORECASE
    )

    # Common URL schemes
    URL_SCHEMES = ['http://', 'https://', 'ftp://', 'www.']

    @staticmethod
    def detect_type(text):
        """
        Detect content type from clipboard text.

        Args:
            text: The clipboard text content

        Returns:
            str: 'link' or 'text'
        """
        text = text.strip()

        # Check 1: Direct URL match
        if ContentDetector.URL_PATTERN.match(text):
            return 'link'

        # Check 2: Text contains a single URL and not much else
        urls = re.findall(r'https?://\S+', text)
        if urls and len(urls) == 1 and len(text) < len(urls[0]) + 10:
            return 'link'

        # Check 3: Starts with common URL schemes
        for scheme in ContentDetector.URL_SCHEMES:
            if text.lower().startswith(scheme):
                # Make sure it's mostly a URL
                if '\n' not in text and len(text) < 500:
                    return 'link'

        return 'text'

    @staticmethod
    def get_type_description(content_type):
        """Get a human-readable description of the content type."""
        descriptions = {
            'text':  'Plain Text',
            'link':  'URL / Link',
            'image': 'Image File',
        }
        return descriptions.get(content_type, 'Unknown')