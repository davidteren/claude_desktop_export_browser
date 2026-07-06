#!/usr/bin/env python3
"""Self-check for get_message_text (issue #3 follow-up: unsupported-block placeholders)."""
from claude_chat_browser import ClaudeChatBrowser

get_message_text = ClaudeChatBrowser.get_message_text
PLACEHOLDER = ClaudeChatBrowser.UNSUPPORTED_BLOCK_TEXT


def main():
    # Structured content: text blocks joined, tool blocks skipped
    msg = {
        'text': f"Reading file{PLACEHOLDER}Done reading.",
        'content': [
            {'type': 'text', 'text': 'Reading file'},
            {'type': 'tool_use', 'name': 'bash', 'input': {}},
            {'type': 'tool_result', 'content': [{'type': 'text', 'text': 'raw output'}]},
            {'type': 'text', 'text': 'Done reading.'},
        ],
    }
    assert get_message_text(msg) == 'Reading file\n\nDone reading.'

    # Markdown-significant indentation inside a block is preserved
    msg = {'content': [{'type': 'text', 'text': '\n- item\n    - nested\n'}]}
    assert get_message_text(msg) == '- item\n    - nested'

    # Legacy flattened text: placeholders stripped — bare line, plain fence, fence with language tag
    msg = {'text': f"Before\n```\n{PLACEHOLDER}\n```\nMid\n```text\n{PLACEHOLDER}\n```\n{PLACEHOLDER}\nAfter"}
    out = get_message_text(msg)
    assert PLACEHOLDER not in out
    assert '```' not in out
    assert 'Before' in out and 'Mid' in out and 'After' in out

    # Inline placeholder doesn't glue surrounding words together
    out = get_message_text({'text': f"end.{PLACEHOLDER}Next"})
    assert out == 'end. Next'

    # Plain message untouched
    assert get_message_text({'text': 'hello'}) == 'hello'
    assert get_message_text({}) == ''

    print('ok')


if __name__ == '__main__':
    main()
