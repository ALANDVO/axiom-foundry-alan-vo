"""Platform-specific configuration generators for AI coding agents.

Each platform (Claude Code, Cursor, OpenCode, etc.) has its own configuration format.
This module generates the appropriate config JSON from a Skill's stored config.
"""

from typing import Any


def generate_claude_code_config(skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate Claude Code skill configuration.

    Expected skill.config keys:
    - `command`: The command to run (e.g., "python", "node")
    - `args`: List of arguments
    - `env`: Environment variables dict
    - `cwd`: Working directory
    - `timeout`: Timeout in seconds
    """
    return {
        "name": skill_config.get("name", ""),
        "description": skill_config.get("description", ""),
        "command": skill_config.get("command", ""),
        "args": skill_config.get("args", []),
        "env": skill_config.get("env", {}),
        "cwd": skill_config.get("cwd", ""),
        "timeout": skill_config.get("timeout", 300),
    }


def generate_cursor_config(skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate Cursor skill configuration.

    Expected skill.config keys:
    - `command`: The command to run
    - `args`: List of arguments
    - `env`: Environment variables dict
    - `cwd`: Working directory
    - `hotkey`: Keyboard shortcut (optional)
    """
    return {
        "name": skill_config.get("name", ""),
        "description": skill_config.get("description", ""),
        "command": skill_config.get("command", ""),
        "args": skill_config.get("args", []),
        "env": skill_config.get("env", {}),
        "cwd": skill_config.get("cwd", ""),
        "hotkey": skill_config.get("hotkey", ""),
    }


def generate_opencode_config(skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate OpenCode skill configuration.

    Expected skill.config keys:
    - `command`: The command to run
    - `args`: List of arguments
    - `env`: Environment variables dict
    - `cwd`: Working directory
    """
    return {
        "name": skill_config.get("name", ""),
        "description": skill_config.get("description", ""),
        "command": skill_config.get("command", ""),
        "args": skill_config.get("args", []),
        "env": skill_config.get("env", {}),
        "cwd": skill_config.get("cwd", ""),
    }


def generate_codex_config(skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate Codex skill configuration.

    Expected skill.config keys:
    - `prompt`: The prompt template
    - `model`: Model to use (optional)
    - `temperature`: Temperature (optional)
    - `max_tokens`: Max tokens (optional)
    """
    return {
        "name": skill_config.get("name", ""),
        "description": skill_config.get("description", ""),
        "prompt": skill_config.get("prompt", ""),
        "model": skill_config.get("model", "gpt-4"),
        "temperature": skill_config.get("temperature", 0.7),
        "max_tokens": skill_config.get("max_tokens", 4000),
    }


def generate_gemini_config(skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate Gemini skill configuration.

    Expected skill.config keys:
    - `prompt`: The prompt template
    - `model`: Model to use (optional)
    - `temperature`: Temperature (optional)
    - `max_output_tokens`: Max output tokens (optional)
    """
    return {
        "name": skill_config.get("name", ""),
        "description": skill_config.get("description", ""),
        "prompt": skill_config.get("prompt", ""),
        "model": skill_config.get("model", "gemini-1.5-pro"),
        "temperature": skill_config.get("temperature", 0.7),
        "max_output_tokens": skill_config.get("max_output_tokens", 4000),
    }


def generate_zed_config(skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate Zed skill configuration.

    Expected skill.config keys:
    - `command`: The command to run
    - `args`: List of arguments
    - `env`: Environment variables dict
    - `cwd`: Working directory
    """
    return {
        "name": skill_config.get("name", ""),
        "description": skill_config.get("description", ""),
        "command": skill_config.get("command", ""),
        "args": skill_config.get("args", []),
        "env": skill_config.get("env", {}),
        "cwd": skill_config.get("cwd", ""),
    }


# Map platform names to generator functions
PLATFORM_GENERATORS: dict[str, callable] = {
    "claude": generate_claude_code_config,
    "claude-code": generate_claude_code_config,
    "cursor": generate_cursor_config,
    "opencode": generate_opencode_config,
    "codex": generate_codex_config,
    "gemini": generate_gemini_config,
    "zed": generate_zed_config,
}


def generate_platform_config(platform: str, skill_config: dict[str, Any]) -> dict[str, Any]:
    """Generate platform-specific configuration for a skill.

    Args:
        platform: Platform name (claude, cursor, opencode, codex, gemini, zed)
        skill_config: The skill's stored config dict

    Returns:
        Platform-specific configuration dict

    Raises:
        ValueError: If platform is not supported
    """
    generator = PLATFORM_GENERATORS.get(platform.lower())
    if not generator:
        supported = ", ".join(sorted(set(PLATFORM_GENERATORS.keys())))
        raise ValueError(
            f"Unsupported platform: '{platform}'. Supported platforms: {supported}"
        )
    return generator(skill_config)


def get_supported_platforms() -> list[str]:
    """Return list of supported platform names."""
    return sorted(set(PLATFORM_GENERATORS.keys()))
