# Claude Chat History Browser

A command-line tool for browsing, searching, and exporting Claude AI assistant conversations from data exports.

![Claude Chat Browser Screenshot](https://via.placeholder.com/800x450.png?text=Claude+Chat+Browser+Screenshot)

## Features

- **Browse Conversations**: Navigate through your Claude chat history with an easy-to-use interface
- **Pagination**: View conversations 10 at a time with simple navigation
- **Export Options**: Export conversations in both Markdown and JSON formats
- **Chronological Sorting**: Messages are automatically sorted by timestamp for readability
- **Preview Content**: View conversation details before exporting
- **No Dependencies**: Uses only Python standard libraries

## Installation

No installation required! Simply:

1. Download this repository
2. Make sure you have a Claude data export in the same directory (format: `data-YYYY-MM-DD-HH-MM-SS/`)
3. Ensure you have Python 3.6+ installed

## Usage

```bash
# Make the script executable (if needed)
chmod +x claude_chat_browser.py

# Run the browser
./claude_chat_browser.py
```

### Navigation Controls

- **Up/Down Arrow Keys**: Navigate through conversations
- **Left/Right Arrow Keys**: Change pages
- **Enter**: Select a conversation and view details
- **Y/N**: Confirm or cancel export
- **Q**: Quit the browser

## Export Format

Conversations are exported to the `exports/` directory with two files for each conversation:

1. **Markdown (.md)**: Human-readable format with timestamps and formatted messages
2. **JSON (.json)**: Complete conversation data in machine-readable format

## How to Get Claude Data Exports

1. In the Claude Desktop app or web interface, go to your account settings
2. Look for "Export Data" or similar option
3. Download the ZIP file and extract it
4. Place the extracted folder (named like `data-2025-03-02-15-59-23`) in the same directory as this tool

## Development

Want to contribute or extend the functionality? Check out the `CLAUDE.md` file for development guidelines and code style information.

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Built for the Claude AI assistant community
- Inspired by the need for better ways to browse and reference past conversations