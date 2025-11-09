# PrivateBin MCP Server

A Model Context Protocol (MCP) server for secure encrypted sharing via [PrivateBin](https://privatebin.info/). This server enables AI assistants to create and retrieve encrypted shares while maintaining strong security boundaries.

## 🔒 Security Features

- **Server URL Control**: The PrivateBin server URL is configured via environment variable and cannot be overridden by the AI agent (prevents data exfiltration)
- **Hidden Passcodes**: Default passcode is stored in environment variable, not visible to the LLM
- **File-based Decryption**: Decrypted content is written to files, not returned to the agent (keeps sensitive data hidden from LLMs)
- **End-to-end Encryption**: All content is encrypted locally before being sent to the server

## Installation

### Using uvx (recommended)

```bash
uvx privatebin-mcp
```

### Using pip

```bash
pip install privatebin-mcp
```

### From source

```bash
git clone https://github.com/aaronsteers/privatebin-mcp.git
cd privatebin-mcp
uv sync
```

## Configuration

### Required Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required: PrivateBin server URL
PRIVATEBIN_SERVER_URL=https://privatebin.net

# Optional: Default passcode for additional security
PRIVATEBIN_DEFAULT_PASSCODE=your-secret-passcode
```

### MCP Client Configuration

Add this server to your MCP client configuration (e.g., Claude Desktop, Devin):

```json
{
  "mcpServers": {
    "privatebin": {
      "command": "uvx",
      "args": ["privatebin-mcp"],
      "env": {
        "PRIVATEBIN_SERVER_URL": "https://privatebin.net",
        "PRIVATEBIN_DEFAULT_PASSCODE": "optional-default-passcode"
      }
    }
  }
}
```

Or if installed from source:

```json
{
  "mcpServers": {
    "privatebin": {
      "command": "uv",
      "args": ["run", "privatebin-mcp"],
      "cwd": "/path/to/privatebin-mcp",
      "env": {
        "PRIVATEBIN_SERVER_URL": "https://privatebin.net",
        "PRIVATEBIN_DEFAULT_PASSCODE": "optional-default-passcode"
      }
    }
  }
}
```

## Available Tools

### 1. `create_encrypted_share_from_string`

Create and post an encrypted paste from string content.

**Parameters:**
- `content` (string, required): Text content to encrypt and share
- `format` (string, optional): Format type - `plaintext`, `syntaxhighlighting`, or `markdown` (default: `plaintext`)
- `expiration` (string, optional): Expiration time - `5min`, `10min`, `1hour`, `1day`, `1week`, `1month`, `1year`, or `never` (default: `1week`)
- `burn_after_reading` (boolean, optional): Delete after first view (default: `false`)
- `enable_discussion` (boolean, optional): Enable comments (default: `false`)
- `passcode` (string, optional): Additional passcode protection (falls back to `PRIVATEBIN_DEFAULT_PASSCODE`)

**Returns:** Full PrivateBin URL with encryption key

**Example:**
```python
# AI assistant creates an encrypted share
url = create_encrypted_share_from_string(
    content="Secret information here",
    format="markdown",
    expiration="1day",
    burn_after_reading=True,
    passcode="optional-extra-security"
)
# Returns: https://privatebin.net/?abc123#encryptionkey
```

### 2. `create_encrypted_share_from_file`

Create and post an encrypted paste from file contents.

**Parameters:**
- `file_path` (string, required): Path to file to encrypt and share
- Same optional parameters as `create_encrypted_share_from_string`

**Returns:** Full PrivateBin URL with encryption key

**Example:**
```python
# AI assistant shares a file
url = create_encrypted_share_from_file(
    file_path="/path/to/document.txt",
    format="plaintext",
    expiration="1week"
)
```

### 3. `save_decrypted_share_to_file`

Retrieve and decrypt a PrivateBin share, saving it to a file.

**Parameters:**
- `url` (string, required): Full PrivateBin URL (with fragment)
- `output_path` (string, required): Path where to save decrypted content
- `passcode` (string, optional): Passcode if the share is protected (falls back to `PRIVATEBIN_DEFAULT_PASSCODE`)

**Returns:** Success message with file path (does NOT include decrypted content)

**Example:**
```python
# AI assistant retrieves and saves a share
result = save_decrypted_share_to_file(
    url="https://privatebin.net/?abc123#encryptionkey",
    output_path="/path/to/output.txt",
    passcode="optional-passcode"
)
# Returns: "Successfully saved decrypted content to: /path/to/output.txt (1234 characters)"
# Note: The actual content is NOT returned to the AI - only written to the file
```

## Use Cases

### 1. Secure Information Sharing

AI assistants can create encrypted shares of sensitive information without the data being visible in the conversation:

```
User: "Share this API key securely: sk-abc123..."
AI: Creates encrypted share with burn_after_reading=True
    Returns URL to user
    API key never appears in conversation history
```

### 2. Temporary Code Snippets

Share code snippets with automatic expiration:

```
AI: Creates share with format="syntaxhighlighting", expiration="1hour"
    Perfect for temporary code reviews or debugging sessions
```

### 3. Secure File Transfer

Transfer files between systems securely:

```
AI: Reads file, creates encrypted share, provides URL
User: Downloads from another system
AI: Can retrieve and save to different location if needed
```

## Security Model

### What the AI Can Do
- ✅ Create encrypted shares from strings or files
- ✅ Retrieve and save shares to files
- ✅ Specify format, expiration, and other paste options

### What the AI Cannot Do
- ❌ Choose the PrivateBin server (configured via env var)
- ❌ See the default passcode (configured via env var)
- ❌ See decrypted content when retrieving shares (written to file only)

This security model ensures that:
1. **No data exfiltration**: AI cannot send data to arbitrary servers
2. **Hidden credentials**: Passcodes remain invisible to the LLM
3. **Controlled access**: Decrypted content goes to files, not conversation history

## Development

For development setup, testing, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## How It Works

1. **Local Encryption**: Content is encrypted locally using AES-256-GCM before being sent
2. **Server Storage**: Only encrypted data is stored on the PrivateBin server
3. **Key in URL**: The encryption key is included in the URL fragment (after `#`), which is never sent to the server
4. **Secure Sharing**: Share the complete URL with recipients who can decrypt the content in their browser or via this MCP server

## Related Projects

- [PrivateBin](https://github.com/PrivateBin/PrivateBin) - The server software
- [privatebin Python library](https://github.com/Ravencentric/privatebin) - Python client library (used by this MCP server)
- [privatebin-cli](https://github.com/aaronsteers/privatebin-cli) - Command-line tool for PrivateBin

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Aaron Steers** - [GitHub](https://github.com/aaronsteers)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/aaronsteers/privatebin-mcp/issues) on GitHub.
