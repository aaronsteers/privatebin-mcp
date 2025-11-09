"""PrivateBin MCP server implementation.

This module provides an MCP server for secure encrypted sharing via PrivateBin,
with security-focused design that prevents data exfiltration and keeps sensitive
information hidden from LLMs.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastmcp import FastMCP
from privatebin import Expiration, Formatter, create, get
from pydantic import Field

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

app = FastMCP("PrivateBin MCP Server")


def _get_server_url() -> str:
    """Get and validate the PrivateBin server URL from environment."""
    server_url = os.getenv("PRIVATEBIN_SERVER_URL")
    if not server_url:
        raise RuntimeError(
            "PRIVATEBIN_SERVER_URL environment variable is required. "
            "Please set it to your PrivateBin server URL (e.g., https://privatebin.net)"
        )
    return server_url


def _get_default_passcode() -> str:
    """Get the default passcode from environment (may be empty)."""
    return os.getenv("PRIVATEBIN_DEFAULT_PASSCODE", "")


def _create_paste_internal(
    content: str,
    format: str = "plaintext",
    expiration: str = "1week",
    burn_after_reading: bool = False,
    enable_discussion: bool = False,
    passcode: str | None = None,
) -> str:
    """Internal helper to create an encrypted paste.

    Args:
        content: Text content to encrypt and share
        format: Format type (plaintext, syntaxhighlighting, markdown)
        expiration: When the paste expires (5min to never)
        burn_after_reading: Delete after first view
        enable_discussion: Enable comments
        passcode: Optional passcode (falls back to default)

    Returns:
        Full PrivateBin URL with encryption key in fragment
    """
    server_url = _get_server_url()
    effective_passcode = passcode or _get_default_passcode()

    formatter_map = {
        "plaintext": Formatter.PLAIN_TEXT,
        "syntaxhighlighting": Formatter.SYNTAX_HIGHLIGHTING,
        "markdown": Formatter.MARKDOWN,
    }
    formatter_enum = formatter_map.get(format, Formatter.PLAIN_TEXT)

    expiration_map = {
        "5min": Expiration.FIVE_MINUTES,
        "10min": Expiration.TEN_MINUTES,
        "1hour": Expiration.ONE_HOUR,
        "1day": Expiration.ONE_DAY,
        "1week": Expiration.ONE_WEEK,
        "1month": Expiration.ONE_MONTH,
        "1year": Expiration.ONE_YEAR,
        "never": Expiration.NEVER,
    }
    expiration_enum = expiration_map.get(expiration, Expiration.ONE_WEEK)

    result = create(
        text=content,
        server=server_url,
        password=effective_passcode if effective_passcode else None,
        expiration=expiration_enum,
        burn_after_reading=burn_after_reading,
        open_discussion=enable_discussion,
        formatter=formatter_enum,
    )

    return result.url


@app.tool()
def create_encrypted_share_from_string(
    content: Annotated[str, Field(description="Text content to encrypt and share")],
    format: Annotated[
        str,
        Field(
            description="Format type for the paste",
            pattern="^(plaintext|syntaxhighlighting|markdown)$",
        ),
    ] = "plaintext",
    expiration: Annotated[
        str,
        Field(
            description="Expiration time for the paste",
            pattern="^(5min|10min|1hour|1day|1week|1month|1year|never)$",
        ),
    ] = "1week",
    burn_after_reading: Annotated[
        bool, Field(description="Delete paste after first view")
    ] = False,
    enable_discussion: Annotated[
        bool, Field(description="Enable comments/discussion on the paste")
    ] = False,
    passcode: Annotated[
        str | None,
        Field(
            description="Optional passcode for additional protection (falls back to PRIVATEBIN_DEFAULT_PASSCODE env var)"
        ),
    ] = None,
) -> str:
    """Create and post an encrypted paste from string content.

    This tool encrypts content locally and posts it to PrivateBin. The server URL
    is configured via PRIVATEBIN_SERVER_URL environment variable and cannot be
    overridden by the agent (security feature to prevent data exfiltration).

    Returns:
        Full PrivateBin URL with encryption key in fragment
    """
    logger.info(
        f"Creating encrypted share: format={format}, expiration={expiration}, "
        f"burn={burn_after_reading}, discussion={enable_discussion}"
    )

    try:
        url = _create_paste_internal(
            content=content,
            format=format,
            expiration=expiration,
            burn_after_reading=burn_after_reading,
            enable_discussion=enable_discussion,
            passcode=passcode,
        )
        logger.info(f"Successfully created encrypted share: {url}")
        return url

    except Exception as e:
        logger.error(f"Failed to create encrypted share: {e}")
        raise RuntimeError(f"Failed to create encrypted share: {e}") from e


@app.tool()
def create_encrypted_share_from_file(
    file_path: Annotated[str, Field(description="Path to file to encrypt and share")],
    format: Annotated[
        str,
        Field(
            description="Format type for the paste",
            pattern="^(plaintext|syntaxhighlighting|markdown)$",
        ),
    ] = "plaintext",
    expiration: Annotated[
        str,
        Field(
            description="Expiration time for the paste",
            pattern="^(5min|10min|1hour|1day|1week|1month|1year|never)$",
        ),
    ] = "1week",
    burn_after_reading: Annotated[
        bool, Field(description="Delete paste after first view")
    ] = False,
    enable_discussion: Annotated[
        bool, Field(description="Enable comments/discussion on the paste")
    ] = False,
    passcode: Annotated[
        str | None,
        Field(
            description="Optional passcode for additional protection (falls back to PRIVATEBIN_DEFAULT_PASSCODE env var)"
        ),
    ] = None,
) -> str:
    """Create and post an encrypted paste from file contents.

    This tool reads a file, encrypts its contents locally, and posts it to PrivateBin.
    The server URL is configured via PRIVATEBIN_SERVER_URL environment variable.

    Returns:
        Full PrivateBin URL with encryption key in fragment
    """
    logger.info(f"Creating encrypted share from file: {file_path}")

    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")
        logger.info(f"Read {len(content)} characters from {file_path}")

        url = _create_paste_internal(
            content=content,
            format=format,
            expiration=expiration,
            burn_after_reading=burn_after_reading,
            enable_discussion=enable_discussion,
            passcode=passcode,
        )
        logger.info(f"Successfully created encrypted share from file: {url}")
        return url

    except Exception as e:
        logger.error(f"Failed to create encrypted share from file: {e}")
        raise RuntimeError(f"Failed to create encrypted share from file: {e}") from e


@app.tool()
def save_decrypted_share_to_file(
    url: Annotated[str, Field(description="Full PrivateBin URL (with fragment)")],
    output_path: Annotated[
        str, Field(description="Path where to save decrypted content")
    ],
    passcode: Annotated[
        str | None,
        Field(
            description="Passcode if the share is protected (falls back to PRIVATEBIN_DEFAULT_PASSCODE env var)"
        ),
    ] = None,
) -> str:
    """Retrieve and decrypt a PrivateBin share, saving it to a file.

    This tool retrieves an encrypted paste from PrivateBin, decrypts it locally,
    and saves the content to a file. The decrypted content is NOT returned to the
    agent - it's only written to the file (security feature to keep sensitive data
    hidden from LLMs).

    Returns:
        Success message with file path (does not include decrypted content)
    """
    logger.info(f"Retrieving and decrypting share from: {url}")

    try:
        effective_passcode = passcode or _get_default_passcode()

        paste = get(url, password=effective_passcode if effective_passcode else None)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(paste.text, encoding="utf-8")

        logger.info(f"Successfully saved decrypted content to: {output_path}")
        return f"Successfully saved decrypted content to: {output_path} ({len(paste.text)} characters)"

    except Exception as e:
        logger.error(f"Failed to retrieve and decrypt share: {e}")
        raise RuntimeError(f"Failed to retrieve and decrypt share: {e}") from e


def main() -> None:
    """Main entry point for the PrivateBin MCP server."""
    try:
        server_url = _get_server_url()
    except RuntimeError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60, flush=True, file=sys.stderr)
    print("Starting PrivateBin MCP server.", file=sys.stderr)
    print(f"Server URL: {server_url}", file=sys.stderr)
    print("=" * 60, flush=True, file=sys.stderr)

    try:
        asyncio.run(app.run_stdio_async(show_banner=False))
    except KeyboardInterrupt:
        print("PrivateBin MCP server interrupted by user.", file=sys.stderr)
    except Exception as ex:
        print(f"Error running PrivateBin MCP server: {ex}", file=sys.stderr)
        sys.exit(1)

    print("PrivateBin MCP server stopped.", file=sys.stderr)
    print("=" * 60, flush=True, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
