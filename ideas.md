# simple-stdio MCP — Quick Reference

> **Server:** MCP Server Patterns · **v1.0.0** · Transport: Streamable HTTP

---

## Available Tools

| Tool | Input | Description |
|------|-------|-------------|
| `get_server_info` | — | Returns server name, version, transport, status |
| `calculate` | `expression: str` | Evaluates arithmetic: `+`, `-`, `*`, `/`, parentheses |
| `generate_uuid` | — | Generates a new UUID v4 |
| `generate_slug` | `text: str` | Converts text to a URL-friendly slug |
| `reverse_text` | `text: str` | Reverses the supplied string |
| `inspect_text` | `text: str` | Returns basic text stats (char count, word count, etc.) |
| `json_format` | `data: str` | Parses and pretty-prints a JSON string |
| `validate_email` | `email: str` | Basic email address format validation |

---

## Ideas for Additional Tools

### String / Text
- `base64_encode` / `base64_decode` — encode or decode Base64 strings
- `hash_text` — return MD5 / SHA-256 / SHA-512 of a string
- `truncate_text` — trim to N chars with optional ellipsis
- `count_tokens` — estimate LLM token count (tiktoken-style)
- `detect_language` — basic language identification

### Data Utilities
- `csv_to_json` / `json_to_csv` — convert between formats
- `flatten_json` — collapse nested JSON to dot-notation keys
- `diff_json` — show key-level diff between two JSON blobs
- `yaml_to_json` / `json_to_yaml` — YAML ↔ JSON conversion

### Identifiers & Encoding
- `generate_nanoid` — URL-safe compact unique IDs
- `generate_cuid` — collision-resistant IDs (good for DBs)
- `url_encode` / `url_decode` — percent-encode/decode strings
- `generate_otp` — time-based or random OTP for testing

### Validation
- `validate_url` — check URL format + optional reachability flag
- `validate_json_schema` — validate a JSON blob against a JSON Schema
- `validate_cron` — parse and describe a cron expression
- `validate_semver` — check if a string is a valid semantic version

### Math & Conversion
- `convert_units` — e.g. km→miles, Celsius→Fahrenheit, bytes→MB
- `calculate_advanced` — support `sqrt`, `pow`, `log`, `sin/cos/tan`
- `generate_random_number` — min/max range, optional seed

### Date & Time
- `timestamp_to_human` — Unix timestamp → readable datetime
- `human_to_timestamp` — parse date string → Unix timestamp
- `date_diff` — difference between two dates in days/hours/minutes
- `timezone_convert` — convert a datetime between timezones

### DevOps / Python-relevant
- `parse_stack_trace` — extract structured info from a Python traceback
- `regex_test` — test a regex pattern against a string, return matches
- `render_template` — simple Jinja2-style `{{ var }}` substitution
- `format_bytes` — convert raw byte count to human-readable (KB, MB, GB)