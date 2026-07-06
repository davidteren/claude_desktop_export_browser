#!/usr/bin/env python3
"""Self-check for get_message_text (issue #3 follow-up: unsupported-block placeholders)."""
from claude_chat_browser import get_message_text, UNSUPPORTED_BLOCK_TEXT


def main():
    # Structured content: text blocks joined, tool blocks skipped
    msg = {
        'text': f"Reading file{UNSUPPORTED_BLOCK_TEXT}Done reading.",
        'content': [
            {'type': 'text', 'text': 'Reading file'},
            {'type': 'tool_use', 'name': 'bash', 'input': {}},
            {'type': 'tool_result', 'content': [{'type': 'text', 'text': 'raw output'}]},
            {'type': 'text', 'text': 'Done reading.'},
        ],
    }
    assert get_message_text(msg) == 'Reading file\n\nDone reading.'

    # Legacy flattened text only: placeholders stripped, fenced or bare
    msg = {'text': f"Before\n```\n{UNSUPPORTED_BLOCK_TEXT}\n```\nAfter {UNSUPPORTED_BLOCK_TEXT}"}
    out = get_message_text(msg)
    assert UNSUPPORTED_BLOCK_TEXT not in out
    assert '```' not in out
    assert 'Before' in out and 'After' in out

    # Plain message untouched
    assert get_message_text({'text': 'hello'}) == 'hello'
    assert get_message_text({}) == ''

    print('ok')


if __name__ == '__main__':
    main()
