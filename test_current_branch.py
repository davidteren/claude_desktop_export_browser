#!/usr/bin/env python3
"""Self-check for get_current_branch (PR #6: rebuild the active branch of
Claude's branching message tree, dropping superseded retries/edits)."""
from claude_chat_browser import ClaudeChatBrowser

get_current_branch = ClaudeChatBrowser.get_current_branch


def msg(uid, parent, t, **extra):
    """Minimal message node. `t` is an hour offset used only for ordering."""
    m = {
        'uuid': uid,
        'parent_message_uuid': parent,
        'created_at': f"2026-01-01T{t:02d}:00:00Z",
    }
    m.update(extra)
    return m


def uuids(branch):
    return [m.get('uuid') for m in branch]


def main():
    # Empty input
    assert get_current_branch([]) == []

    # Single linear chain — returned root-to-leaf, in order
    chain = [
        msg('r', None, 0),
        msg('a', 'r', 1),
        msg('b', 'a', 2),
        msg('c', 'b', 3),
    ]
    assert uuids(get_current_branch(chain)) == ['r', 'a', 'b', 'c']

    # Retry branch: 'a' has two children. The abandoned reply 'x' is a leaf;
    # the active branch 'b'->'c' is deeper AND its messages carry an *earlier*
    # timestamp than the retry. Depth must win over timestamp, and the
    # abandoned turn must be dropped entirely.
    branched = [
        msg('r', None, 0),
        msg('a', 'r', 1),
        msg('b', 'a', 2),          # active, older
        msg('c', 'b', 3),
        msg('x', 'a', 9),          # abandoned retry, newer but shallower
    ]
    out = uuids(get_current_branch(branched))
    assert out == ['r', 'a', 'b', 'c'], out
    assert 'x' not in out

    # Messages without a uuid must not crash (skipped from the index, still
    # tolerated as standalone roots rather than blowing up).
    with_none = [
        msg('r', None, 0),
        msg('a', 'r', 1),
        {'created_at': '2026-01-01T05:00:00Z', 'text': 'no uuid'},
    ]
    out = get_current_branch(with_none)
    assert 'r' in uuids(out) and 'a' in uuids(out)
    assert len(out) == 3  # nothing dropped, no crash

    # No valid roots (every node's parent is present → a pure cycle):
    # fall back to a flat chronological sort instead of dropping everything.
    cyclic = [
        msg('p', 'q', 2),
        msg('q', 'p', 1),
    ]
    out = get_current_branch(cyclic)
    assert set(uuids(out)) == {'p', 'q'}          # nothing lost
    assert uuids(out) == ['q', 'p']               # sorted by created_at

    # Multiple disconnected fragments (a second root appears partway through):
    # each fragment's deepest path is concatenated, roots ordered by created_at.
    fragments = [
        msg('r2', None, 5),        # later root
        msg('s2', 'r2', 6),
        msg('r1', None, 0),        # earlier root
        msg('s1', 'r1', 1),
    ]
    assert uuids(get_current_branch(fragments)) == ['r1', 's1', 'r2', 's2']

    print('ok')


if __name__ == '__main__':
    main()
