# Claude Chat History Browser - Assistant Guide

## Project Overview
This project provides tools for browsing and exporting Claude AI assistant chat histories from desktop/browser exports. The primary tool is a terminal-based browser that allows users to navigate and export conversations.

## Tools & Commands
- **Chat Browser**: `./claude_chat_browser.py` - Interactive CLI for browsing and exporting chats
- **Installation**: No additional dependencies required (uses standard Python libraries)
- **Usage**: Simply run the script in a directory containing Claude data exports

## Code Style Guidelines
- **Formatting**: Use consistent indentation (4 spaces for Python)
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Imports**: Group imports in the following order:
  1. Standard library imports
  2. Third-party library imports (if any are added in the future)
  3. Local application imports
- **Types**: Use type hints for function parameters and return values
- **Comments**: Use docstrings for classes and functions following the Google style
- **Error Handling**: Use try/except blocks with specific exception types
- **Architecture**: Follow object-oriented design with clear separation of concerns

## Chat Browser Features
- Browse conversations chronologically (newest first)
- Pagination with 10 items per page
- View conversation details and preview content
- Export selected conversations in both Markdown and JSON formats to the exports/ directory
  - Messages are sorted chronologically with timestamps
  - Preserves complete conversation data in JSON format
  - Creates human-readable Markdown alongside machine-readable JSON
- Navigation using arrow keys and keyboard shortcuts
- Automatic detection of most recent Claude data export directory

## Development Guidelines
- Add new features by extending the ClaudeChatBrowser class
- Use curses for terminal-based UI components
- Maintain backward compatibility with existing Claude export format
- Handle exceptions gracefully with user-friendly error messages
- When adding new export formats, maintain the dual approach of human-readable + machine-readable
- Test with various Claude data export formats to ensure compatibility