def register_tools(mcp):
    # No arguments → simple tool
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def get_server_info() -> dict:
        """Return information about the MCP server."""
        return {
            "name": "MCP Server Patterns",
            "version": "1.0.0",
            "transport": "Streamable HTTP",
            "status": "running",
        }

    # Typed arguments → tool schema
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def calculate(expression: str) -> str:
        """
        Evaluate a basic mathematical expression.

        Supports arithmetic operations such as +, -, *, / and parentheses.
        """
        try:
            # Keep this intentionally simple for a demo.
            allowed = set("0123456789+-*/(). ")

            if not set(expression) <= allowed:
                return "Invalid expression. Only basic arithmetic is supported."

            result = eval(expression, {"__builtins__": {}}, {})

            return str(result)

        except Exception as exc:
            return f"Calculation error: {exc}"

    # Structured input/output → realistic tool
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def inspect_text(text: str) -> dict:
        """
        Analyze a text string and return basic statistics.
        """
        lines = text.splitlines()
        words = text.split()

        return {
            "characters": len(text),
            "words": len(words),
            "lines": len(lines),
            "empty": not bool(text.strip()),
        }

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def reverse_text(text: str) -> str:
        """
        Reverse the supplied text.
        """
        return text[::-1]

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def generate_slug(text: str) -> str:
        """
        Convert text into a URL-friendly slug.
        """
        import re

        slug = text.lower().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)

        return slug.strip("-")

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def validate_email(email: str) -> dict:
        """
        Perform basic email address validation.
        """
        import re

        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        valid = bool(re.match(pattern, email))

        return {
            "email": email,
            "valid": valid,
        }

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    def json_format(data: str) -> str:
        """
        Parse and pretty-print a JSON string.
        """
        import json

        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as exc:
            return f"Invalid JSON: {exc}"

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        }
    )
    def generate_uuid() -> str:
        """
        Generate a new UUID.
        """
        import uuid

        return str(uuid.uuid4())
