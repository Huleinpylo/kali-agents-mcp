# Security Review Notes

This document summarizes key security observations for the `kali-agents-mcp` repository.

## Credentials and Configuration

- Example environment file includes default values for secrets such as `MSF_RPC_PASS` and API secrets. These values should never be used in production. [See `.env.example` lines 38-53.]
- The application loads these values using `os.getenv` with default placeholders. [See `src/config/settings.py` lines 60-105.]
- Recommendation: require explicit environment variables and avoid shipping weak defaults.

## Subprocess Usage

- Network and web servers run external tools via `subprocess.run` without using `shell=True`, which mitigates command injection risks. [Example: `src/mcp_servers/network_server.py` lines 25-74.]
- Ensure user-controlled parameters are validated to prevent abuse (e.g., restrict targets to authorized scopes).

## Logging and Secret Handling

- Sensitive secrets such as API keys may appear in log files if logging is too verbose. Logging paths are configurable via `LOGGING_CONFIG` but secrets are not explicitly masked.
- Recommendation: sanitize log output and rotate logs regularly.

## Dependency Security

- Pre-commit configuration integrates Bandit and Safety for static analysis and dependency checks, but these tools are not installed in this environment. [See `.pre-commit-config.yaml` lines 21-45.]
- Ensure CI runs these checks to catch vulnerabilities.

## Suggested Improvements

1. Enforce mandatory environment variables for secrets with no insecure defaults.
2. Implement authorization checks for tool execution as hinted in `SECURITY_IMPLEMENTATION.md`.
3. Add unit tests for subprocess error handling and edge cases.
4. Use a secrets scanner (e.g., detect-secrets) in CI to avoid accidental commits.
5. Document a process for periodic dependency updates and vulnerability scanning.

