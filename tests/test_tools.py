import json
import re
import pytest
from unittest.mock import MagicMock, patch
from typing import Callable
from examples.common.tools import register_tools


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Minimal stand-in for the MCP object so we can collect registered tools."""

    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def tool(self):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            return fn

        return decorator

    def __getitem__(self, name: str):
        return self._tools[name]


@pytest.fixture(scope="module")
def tools():
    """Register all tools once and expose them by name."""
    registry = ToolRegistry()
    register_tools(registry)  # the function under test
    return registry


# ---------------------------------------------------------------------------
# get_server_info
# ---------------------------------------------------------------------------

class TestGetServerInfo:
    def test_returns_dict(self, tools):
        result = tools["get_server_info"]()
        assert isinstance(result, dict)

    def test_required_keys(self, tools):
        result = tools["get_server_info"]()
        assert {"name", "version", "transport", "status"} <= result.keys()

    def test_status_is_running(self, tools):
        assert tools["get_server_info"]()["status"] == "running"

    def test_values_are_strings(self, tools):
        result = tools["get_server_info"]()
        assert all(isinstance(v, str) for v in result.values())


# ---------------------------------------------------------------------------
# calculate
# ---------------------------------------------------------------------------

class TestCalculate:
    @pytest.mark.parametrize("expression, expected", [
        ("2 + 3", "5"),
        ("10 - 4", "6"),
        ("3 * 7", "21"),
        ("10 / 4", "2.5"),
        ("(2 + 3) * 4", "20"),
        ("0", "0"),
        ("100 / 10", "10.0"),
    ])
    def test_valid_expressions(self, tools, expression, expected):
        assert tools["calculate"](expression) == expected

    @pytest.mark.parametrize("expression", [
        "import os",
        "__import__('os')",
        "print('hi')",
        "2 + 2; import sys",
        "a + b",
        "2 ^ 3",
        # "2 ** 3" is valid: * is in the allowed set, eval returns 8
    ])
    def test_invalid_characters_rejected(self, tools, expression):
        result = tools["calculate"](expression)
        assert result.startswith("Invalid expression") or result.startswith("Calculation error")

    def test_division_by_zero(self, tools):
        result = tools["calculate"]("1 / 0")
        assert result.startswith("Calculation error")

    def test_empty_expression(self, tools):
        # eval("") raises SyntaxError → Calculation error
        result = tools["calculate"]("")
        assert result.startswith("Calculation error")

    def test_returns_string(self, tools):
        assert isinstance(tools["calculate"]("1 + 1"), str)


# ---------------------------------------------------------------------------
# inspect_text
# ---------------------------------------------------------------------------

class TestInspectText:
    def test_basic_stats(self, tools):
        result = tools["inspect_text"]("Hello world\nFoo bar")
        assert result == {
            "characters": 19,
            "words": 4,
            "lines": 2,
            "empty": False,
        }

    def test_empty_string(self, tools):
        result = tools["inspect_text"]("")
        assert result["characters"] == 0
        assert result["words"] == 0
        assert result["lines"] == 0  # "".splitlines() → [], len([]) == 0
        assert result["empty"] is True

    def test_whitespace_only_is_empty(self, tools):
        assert tools["inspect_text"]("   \n  \t  ")["empty"] is True

    def test_single_word(self, tools):
        result = tools["inspect_text"]("Python")
        assert result["words"] == 1
        assert result["characters"] == 6

    def test_multiline(self, tools):
        text = "line1\nline2\nline3"
        assert tools["inspect_text"](text)["lines"] == 3

    def test_returns_dict_with_expected_keys(self, tools):
        result = tools["inspect_text"]("x")
        assert {"characters", "words", "lines", "empty"} == result.keys()

    def test_unicode(self, tools):
        result = tools["inspect_text"]("héllo wörld")
        assert result["words"] == 2
        assert result["empty"] is False


# ---------------------------------------------------------------------------
# reverse_text
# ---------------------------------------------------------------------------

class TestReverseText:
    @pytest.mark.parametrize("text, expected", [
        ("hello", "olleh"),
        ("Python", "nohtyP"),
        ("", ""),
        ("a", "a"),
        ("racecar", "racecar"),  # palindrome
        ("hello world", "dlrow olleh"),
        ("12345", "54321"),
    ])
    def test_reverse(self, tools, text, expected):
        assert tools["reverse_text"](text) == expected

    def test_double_reverse_identity(self, tools):
        original = "MCP server"
        assert tools["reverse_text"](tools["reverse_text"](original)) == original

    def test_returns_string(self, tools):
        assert isinstance(tools["reverse_text"]("x"), str)


# ---------------------------------------------------------------------------
# generate_slug
# ---------------------------------------------------------------------------

class TestGenerateSlug:
    @pytest.mark.parametrize("text, expected", [
        ("Hello World", "hello-world"),
        ("  leading spaces  ", "leading-spaces"),
        ("Python & Django!", "python-django"),
        ("multiple   spaces", "multiple-spaces"),
        ("UPPER CASE", "upper-case"),
        ("already-a-slug", "already-a-slug"),
        ("Special @#$% chars", "special-chars"),
        ("", ""),
    ])
    def test_slug_generation(self, tools, text, expected):
        assert tools["generate_slug"](text) == expected

    def test_no_leading_trailing_hyphens(self, tools):
        slug = tools["generate_slug"]("  !!hello!!")
        assert not slug.startswith("-")
        assert not slug.endswith("-")

    def test_slug_contains_only_valid_chars(self, tools):
        slug = tools["generate_slug"]("Hello, World! This is a test.")
        assert re.fullmatch(r"[a-z0-9-]*", slug)

    def test_returns_string(self, tools):
        assert isinstance(tools["generate_slug"]("test"), str)


# ---------------------------------------------------------------------------
# validate_email
# ---------------------------------------------------------------------------

class TestValidateEmail:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "user.name+tag@sub.domain.org",
        "x@y.z",
    ])
    def test_valid_emails(self, tools, email):
        result = tools["validate_email"](email)
        assert result["valid"] is True
        assert result["email"] == email

    @pytest.mark.parametrize("email", [
        "not-an-email",
        "@missing-local.com",
        "missing-at-sign.com",
        "missing@tld",
        "",
        "spaces in@email.com",
        "double@@at.com",
    ])
    def test_invalid_emails(self, tools, email):
        result = tools["validate_email"](email)
        assert result["valid"] is False
        assert result["email"] == email

    def test_returns_dict_with_expected_keys(self, tools):
        result = tools["validate_email"]("a@b.com")
        assert {"email", "valid"} == result.keys()

    def test_valid_flag_is_bool(self, tools):
        assert isinstance(tools["validate_email"]("a@b.com")["valid"], bool)


# ---------------------------------------------------------------------------
# json_format
# ---------------------------------------------------------------------------

class TestJsonFormat:
    def test_formats_object(self, tools):
        raw = '{"b":2,"a":1}'
        result = tools["json_format"](raw)
        # Must be valid JSON and pretty-printed (2-space indent)
        parsed = json.loads(result)
        assert parsed == {"a": 1, "b": 2}
        assert "  " in result  # indented

    def test_formats_array(self, tools):
        result = tools["json_format"]("[1,2,3]")
        assert json.loads(result) == [1, 2, 3]

    def test_preserves_unicode(self, tools):
        raw = '{"greeting":"héllo"}'
        result = tools["json_format"](raw)
        assert "héllo" in result  # ensure_ascii=False

    def test_nested_structure(self, tools):
        raw = '{"a":{"b":{"c":42}}}'
        parsed = json.loads(tools["json_format"](raw))
        assert parsed["a"]["b"]["c"] == 42

    def test_invalid_json_returns_error_string(self, tools):
        result = tools["json_format"]("{not valid json}")
        assert result.startswith("Invalid JSON")

    def test_empty_string_is_invalid(self, tools):
        result = tools["json_format"]("")
        assert result.startswith("Invalid JSON")

    def test_returns_string(self, tools):
        assert isinstance(tools["json_format"]('{"x":1}'), str)


# ---------------------------------------------------------------------------
# generate_uuid
# ---------------------------------------------------------------------------

UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class TestGenerateUuid:
    def test_returns_string(self, tools):
        assert isinstance(tools["generate_uuid"](), str)

    def test_valid_uuid4_format(self, tools):
        uuid = tools["generate_uuid"]()
        assert UUID4_RE.match(uuid), f"Not a valid UUID4: {uuid}"

    def test_uniqueness(self, tools):
        uuids = {tools["generate_uuid"]() for _ in range(1000)}
        assert len(uuids) == 1000

    def test_version_bit(self, tools):
        uuid = tools["generate_uuid"]()
        version_char = uuid[14]  # character after third hyphen
        assert version_char == "4"

    def test_variant_bit(self, tools):
        uuid = tools["generate_uuid"]()
        variant_char = uuid[19]  # first char of the fourth group
        assert variant_char in "89ab"
