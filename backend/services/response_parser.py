"""
ResponseParser Service - Agent Instruction System Phase 2

Parses XML-formatted agent responses into structured data.

Expected response format:
```xml
<thinking>Agent's internal reasoning</thinking>
<message>Response to the writer</message>
<action type="action_name">
  <param>value</param>
</action>
<content_update target="file_path">
  Updated content here
</content_update>
```

Features:
- Extracts <thinking>, <message>, <action>, <content_update> tags
- Graceful fallback for malformed responses
- Action parameter parsing
- Multi-action support (multiple actions per response)
"""

import logging
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParsedAction:
    """A parsed action from agent response."""
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""


@dataclass
class ContentUpdate:
    """A content update from agent response."""
    target: str
    content: str


@dataclass
class ParsedResponse:
    """Complete parsed agent response."""
    thinking: str = ""
    message: str = ""
    actions: List[ParsedAction] = field(default_factory=list)
    content_updates: List[ContentUpdate] = field(default_factory=list)
    raw_response: str = ""
    parse_errors: List[str] = field(default_factory=list)
    used_fallback: bool = False


class ResponseParser:
    """
    Parses XML-formatted agent responses.

    Handles:
    - Well-formed XML responses
    - Partially formed responses (missing some tags)
    - Plain text responses (fallback mode)
    - Multiple actions per response
    """

    # Regex patterns for tag extraction
    THINKING_PATTERN = re.compile(
        r'<thinking>(.*?)</thinking>',
        re.DOTALL | re.IGNORECASE
    )
    MESSAGE_PATTERN = re.compile(
        r'<message>(.*?)</message>',
        re.DOTALL | re.IGNORECASE
    )
    ACTION_PATTERN = re.compile(
        r'<action\s+type=["\']([^"\']+)["\']>(.*?)</action>',
        re.DOTALL | re.IGNORECASE
    )
    CONTENT_UPDATE_PATTERN = re.compile(
        r'<content_update\s+target=["\']([^"\']+)["\']>(.*?)</content_update>',
        re.DOTALL | re.IGNORECASE
    )

    # Action parameter patterns
    PARAM_TAG_PATTERN = re.compile(
        r'<(\w+)>(.*?)</\1>',
        re.DOTALL
    )

    def parse(self, response: str) -> ParsedResponse:
        """
        Parse an agent response.

        Args:
            response: Raw response from the agent

        Returns:
            ParsedResponse with extracted components
        """
        result = ParsedResponse(raw_response=response)

        if not response:
            result.parse_errors.append("Empty response")
            return result

        # Extract thinking
        thinking_match = self.THINKING_PATTERN.search(response)
        if thinking_match:
            result.thinking = self._clean_content(thinking_match.group(1))

        # Extract message
        message_match = self.MESSAGE_PATTERN.search(response)
        if message_match:
            result.message = self._clean_content(message_match.group(1))
        else:
            # Fallback: use entire response as message if no tags found
            if not any([
                self.THINKING_PATTERN.search(response),
                self.ACTION_PATTERN.search(response),
                self.CONTENT_UPDATE_PATTERN.search(response)
            ]):
                result.message = self._clean_content(response)
                result.used_fallback = True
                result.parse_errors.append("No XML tags found, using plain text fallback")

        # Extract actions
        action_matches = self.ACTION_PATTERN.findall(response)
        for action_type, action_content in action_matches:
            action = self._parse_action(action_type, action_content)
            result.actions.append(action)

        # Extract content updates
        update_matches = self.CONTENT_UPDATE_PATTERN.findall(response)
        for target, content in update_matches:
            result.content_updates.append(ContentUpdate(
                target=target.strip(),
                content=self._clean_content(content)
            ))

        return result

    def _parse_action(self, action_type: str, content: str) -> ParsedAction:
        """Parse action parameters from action content."""
        action = ParsedAction(
            action_type=action_type.strip(),
            raw_content=content.strip()
        )

        # Extract parameters using tag pattern
        params = self.PARAM_TAG_PATTERN.findall(content)
        for param_name, param_value in params:
            # Try to parse JSON-like values
            value = self._parse_value(param_value.strip())
            action.params[param_name] = value

        return action

    def _parse_value(self, value: str) -> Any:
        """Parse a parameter value, handling arrays and primitives."""
        if not value:
            return value

        # Remove surrounding whitespace
        value = value.strip()

        # Check for array syntax ["item1", "item2"]
        if value.startswith('[') and value.endswith(']'):
            try:
                # Parse as JSON array
                import json
                return json.loads(value)
            except Exception:
                # Fallback: split by comma
                inner = value[1:-1].strip()
                if inner:
                    items = [item.strip().strip('"\'') for item in inner.split(',')]
                    return items
                return []

        # Check for boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        # Check for integer
        try:
            return int(value)
        except ValueError:
            pass

        # Check for float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _clean_content(self, content: str) -> str:
        """Clean extracted content."""
        if not content:
            return ""

        # Remove leading/trailing whitespace
        content = content.strip()

        # Decode XML entities
        content = (
            content.replace('&lt;', '<')
                   .replace('&gt;', '>')
                   .replace('&amp;', '&')
                   .replace('&quot;', '"')
                   .replace('&apos;', "'")
        )

        return content

    def extract_message_only(self, response: str) -> str:
        """
        Quick extraction of just the message content.

        Useful when you only need the user-facing message.

        Args:
            response: Raw response from agent

        Returns:
            Extracted message or original response
        """
        message_match = self.MESSAGE_PATTERN.search(response)
        if message_match:
            return self._clean_content(message_match.group(1))

        # Fallback: return cleaned response
        # Remove XML-like tags for cleaner output
        cleaned = re.sub(r'<thinking>.*?</thinking>', '', response, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<action.*?>.*?</action>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<content_update.*?>.*?</content_update>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

        return self._clean_content(cleaned)

    def validate_response(self, response: str) -> Dict[str, Any]:
        """
        Validate a response for correct XML formatting.

        Returns:
            Dict with 'valid', 'issues', and 'suggestions'
        """
        issues = []
        suggestions = []

        # Check for message tag
        if not self.MESSAGE_PATTERN.search(response):
            issues.append("Missing <message> tag")
            suggestions.append("Wrap your response in <message>...</message> tags")

        # Check for unclosed tags
        for tag in ['thinking', 'message', 'action', 'content_update']:
            opens = len(re.findall(rf'<{tag}[^>]*>', response, re.IGNORECASE))
            closes = len(re.findall(rf'</{tag}>', response, re.IGNORECASE))
            if opens > closes:
                issues.append(f"Unclosed <{tag}> tag")
            elif closes > opens:
                issues.append(f"Extra </{tag}> closing tag")

        # Check for actions with missing type
        if '<action>' in response.lower() and 'type=' not in response.lower():
            issues.append("Action tag missing type attribute")
            suggestions.append('Use <action type="action_name">...</action>')

        # Check for JSON in actions (should be XML)
        if re.search(r'<action[^>]*>\s*\{', response):
            issues.append("JSON found in action (should use XML parameters)")
            suggestions.append('Use <param>value</param> instead of JSON')

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions
        }


# Singleton instance
_parser: Optional[ResponseParser] = None


def get_response_parser() -> ResponseParser:
    """Get or create the ResponseParser singleton."""
    global _parser
    if _parser is None:
        _parser = ResponseParser()
    return _parser


def parse_agent_response(response: str) -> ParsedResponse:
    """Convenience function to parse an agent response."""
    return get_response_parser().parse(response)


def extract_message(response: str) -> str:
    """Convenience function to extract just the message."""
    return get_response_parser().extract_message_only(response)
