# Claude Chat Export Browser - Development Guide

This document provides information for developers who want to contribute to or modify the Claude Chat Export Browser tool.

## Project Structure

- `claude_chat_browser.py` - Main application file (terminal UI and export functionality)
- `exports/` - Directory where exported conversations are stored
- `docs/` - Documentation for developers
- `CLAUDE.md` - Additional guidelines for Claude AI when working with this codebase

## Architecture

The tool uses a simple object-oriented approach:

- `ClaudeChatBrowser` class handles loading, displaying, and exporting conversations
- `curses` library is used for the terminal UI
- Standard Python libraries are used to keep dependencies minimal

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

## Adding New Features

When extending the functionality, consider the following guidelines:

1. **UI Changes**: Keep the terminal UI simple and intuitive
2. **Export Formats**: Maintain the dual approach of human-readable + machine-readable formats
3. **Backward Compatibility**: Ensure compatibility with existing Claude data export formats
4. **Error Handling**: Add robust error handling for any new functionality

### How to Add a New Export Format

To add a new export format:

1. Create a new method in the `ClaudeChatBrowser` class (follow the pattern of `export_conversation`)
2. Modify the success message display to include the new format
3. Update the documentation to reflect the new export option

## Testing

Currently, the project has no automated tests. When adding tests:

1. Create a `tests/` directory
2. Use Python's standard `unittest` library
3. Add test data (sample conversations) in a `tests/data/` directory

## Future Improvements

Potential areas for enhancement:

- **Search Functionality**: Allow searching for conversations by keyword
- **Filtering**: Add options to filter by date range or conversation length
- **Export Templates**: Customizable templates for Markdown exports
- **Web UI**: A lightweight web interface as an alternative to the terminal UI
- **Batch Operations**: Option to export multiple conversations at once

## Debugging Tips

When debugging the curses UI:

1. Use the `stdscr.addstr(0, 0, f"Debug: {variable}")` approach to display debug info
2. Remember to call `stdscr.refresh()` after adding debug text
3. Handle exceptions and display error messages for easier troubleshooting

## Pull Request Guidelines

When submitting changes:

1. Follow the existing code style and conventions
2. Ensure your changes maintain compatibility with existing features
3. Update documentation to reflect your changes
4. Describe the purpose and implementation details in your PR