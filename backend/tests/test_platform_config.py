import pytest
from app.services.platform_config import (
    generate_claude_code_config,
    generate_cursor_config,
    generate_opencode_config,
    generate_codex_config,
    generate_gemini_config,
    generate_zed_config,
    generate_platform_config,
    get_supported_platforms,
)


class TestPlatformConfigGenerators:
    """Test individual platform config generators."""

    def test_claude_code_config(self):
        skill_config = {
            "name": "test-skill",
            "description": "Test skill",
            "command": "python",
            "args": ["-m", "pytest"],
            "env": {"PYTHONPATH": "."},
            "cwd": "/project",
            "timeout": 600,
        }
        result = generate_claude_code_config(skill_config)
        assert result["name"] == "test-skill"
        assert result["description"] == "Test skill"
        assert result["command"] == "python"
        assert result["args"] == ["-m", "pytest"]
        assert result["env"] == {"PYTHONPATH": "."}
        assert result["cwd"] == "/project"
        assert result["timeout"] == 600

    def test_claude_code_config_defaults(self):
        skill_config = {}
        result = generate_claude_code_config(skill_config)
        assert result["name"] == ""
        assert result["description"] == ""
        assert result["command"] == ""
        assert result["args"] == []
        assert result["env"] == {}
        assert result["cwd"] == ""
        assert result["timeout"] == 300

    def test_cursor_config(self):
        skill_config = {
            "name": "cursor-skill",
            "description": "Cursor skill",
            "command": "node",
            "args": ["script.js"],
            "env": {"NODE_ENV": "development"},
            "cwd": "/workspace",
            "hotkey": "cmd+shift+p",
        }
        result = generate_cursor_config(skill_config)
        assert result["name"] == "cursor-skill"
        assert result["hotkey"] == "cmd+shift+p"

    def test_opencode_config(self):
        skill_config = {
            "name": "opencode-skill",
            "command": "python",
            "args": ["tool.py"],
        }
        result = generate_opencode_config(skill_config)
        assert result["name"] == "opencode-skill"
        assert result["command"] == "python"

    def test_codex_config(self):
        skill_config = {
            "name": "codex-skill",
            "prompt": "Review this code for security issues",
            "model": "gpt-4",
            "temperature": 0.5,
            "max_tokens": 2000,
        }
        result = generate_codex_config(skill_config)
        assert result["name"] == "codex-skill"
        assert result["prompt"] == "Review this code for security issues"
        assert result["model"] == "gpt-4"
        assert result["temperature"] == 0.5
        assert result["max_tokens"] == 2000

    def test_codex_config_defaults(self):
        skill_config = {"prompt": "Test prompt"}
        result = generate_codex_config(skill_config)
        assert result["model"] == "gpt-4"
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 4000

    def test_gemini_config(self):
        skill_config = {
            "name": "gemini-skill",
            "prompt": "Explain this code",
            "model": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_output_tokens": 1000,
        }
        result = generate_gemini_config(skill_config)
        assert result["model"] == "gemini-1.5-flash"
        assert result["max_output_tokens"] == 1000

    def test_zed_config(self):
        skill_config = {
            "name": "zed-skill",
            "command": "rust-analyzer",
            "args": ["--stdio"],
        }
        result = generate_zed_config(skill_config)
        assert result["command"] == "rust-analyzer"

    def test_get_supported_platforms(self):
        platforms = get_supported_platforms()
        assert "claude" in platforms
        assert "claude-code" in platforms
        assert "cursor" in platforms
        assert "opencode" in platforms
        assert "codex" in platforms
        assert "gemini" in platforms
        assert "zed" in platforms
        assert len(platforms) == 7


class TestGeneratePlatformConfig:
    """Test the main generate_platform_config function."""

    def test_generate_claude(self):
        skill_config = {"command": "python", "args": ["test.py"]}
        result = generate_platform_config("claude", skill_config)
        assert result["command"] == "python"

    def test_generate_claude_code_alias(self):
        skill_config = {"command": "python"}
        result = generate_platform_config("claude-code", skill_config)
        assert result["command"] == "python"

    def test_generate_cursor(self):
        skill_config = {"command": "node", "hotkey": "ctrl+k"}
        result = generate_platform_config("cursor", skill_config)
        assert result["hotkey"] == "ctrl+k"

    def test_generate_opencode(self):
        skill_config = {"command": "python"}
        result = generate_platform_config("opencode", skill_config)
        assert result["command"] == "python"

    def test_generate_codex(self):
        skill_config = {"prompt": "Test"}
        result = generate_platform_config("codex", skill_config)
        assert result["prompt"] == "Test"

    def test_generate_gemini(self):
        skill_config = {"prompt": "Test"}
        result = generate_platform_config("gemini", skill_config)
        assert result["prompt"] == "Test"

    def test_generate_zed(self):
        skill_config = {"command": "rust"}
        result = generate_platform_config("zed", skill_config)
        assert result["command"] == "rust"

    def test_case_insensitive(self):
        skill_config = {"command": "test"}
        result = generate_platform_config("CLAUDE", skill_config)
        assert result["command"] == "test"
        result = generate_platform_config("Cursor", skill_config)
        assert result["command"] == "test"

    def test_unsupported_platform(self):
        skill_config = {}
        with pytest.raises(ValueError) as exc_info:
            generate_platform_config("unsupported-platform", skill_config)
        assert "Unsupported platform" in str(exc_info.value)
        assert "claude" in str(exc_info.value)
        assert "cursor" in str(exc_info.value)

