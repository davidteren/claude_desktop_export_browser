# Claude Chat Export Browser
Export your Claude Desktop chats to Markdown and JSON

A simple terminal tool that helps you browse and export conversations from your Claude AI assistant data exports. Get your chat history in both human-readable Markdown and structured JSON formats.

![Claude Chat Export Browser Screenshot](images/claude_chat_exporter.png)

## Quick Start

1. Go to your [Claude account settings and export your data.](https://claude.ai/settings/account)
2. Once you receive the email, download the zip file.
3. Unzip the file and place the extracted folder in the same directory as this tool.
4. Run the tool with `./claude_chat_browser.py`
5. Browse your conversations with arrow keys
6. Press Enter to select a conversation
7. Press Y to export to Markdown and JSON.

## What You Can Do

- **Browse All Conversations**: Newest conversations appear first
- **See Previews**: View the first few messages before exporting
- **Export Easily**: Get both Markdown and JSON versions of any conversation
- **Read Chronologically**: Exported conversations are organized by time with timestamps
- **No Extra Software Needed**: Uses only standard Python libraries

## How to Use

### Step 1: Get Your Claude Data

1. In Claude Desktop app, go to Settings → Export Data
2. Download and extract the ZIP file
3. Place the extracted folder (like `data-2025-03-02-15-59-23`) in the same directory as this tool

### Step 2: Run the Browser

```bash
# Make executable (first time only)
chmod +x claude_chat_browser.py

# Start the browser
./claude_chat_browser.py
```

### Step 3: Navigate and Export

- **Navigate**: Use ↑/↓ arrows to select conversations
- **Change Pages**: Use ←/→ arrows to move between pages (10 conversations per page)
- **View Details**: Press Enter to see conversation details
- **Export**: Press Y when prompted to save as Markdown and JSON
- **Exit**: Press Q to quit

### What You Get

When you export a conversation, two files are created in the `exports/` folder:

- **[date]_[name].md**: Easy-to-read Markdown with all messages in order
- **[date]_[name].json**: Complete structured data you can use in other tools

## Tips

- The tool automatically finds the most recent Claude data export in your directory
- Exported conversations have timestamps so you can see when each message was sent
- Use the JSON exports if you want to process your conversations with other tools

For developer information, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## License

MIT License - See LICENSE file for details.