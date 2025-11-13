# Kali Agents - Specialized Development Agents

This document describes the specialized Claude Code agents available for the Kali Agents project. These agents are designed to accelerate development while maintaining security and quality standards.

## Available Agents

### 1. MCP Security Validator (`mcp-security-validator`)

**Purpose**: Validates security of MCP server implementations and prevents vulnerabilities.

**Use When**:
- Creating or modifying MCP tool functions
- Implementing security tool integrations
- Processing user inputs that reach subprocess calls
- Reviewing parsers for security issues
- Before merging PRs with MCP server changes

**Key Capabilities**:
- Detects command injection vulnerabilities
- Validates input sanitization patterns
- Checks subprocess security (no shell=True)
- Runs bandit security scans
- Verifies Pydantic validation models
- Reviews XML/JSON parser security

**Example Usage**:
```
User: "I added a new nmap tool to the network server"
Claude: [Uses mcp-security-validator to review for command injection]

User: "Ready to merge the sqlmap integration PR"
Claude: [Uses mcp-security-validator to validate security before merge]
```

**Deliverables**:
- Security risk assessment
- Vulnerability findings with severity ratings
- Secure code examples
- Remediation recommendations

---

### 2. Parser Generator (`parser-generator`)

**Purpose**: Generates robust parsers for security tool outputs with comprehensive testing.

**Use When**:
- Integrating a new security tool into an MCP server
- Parser failures on tool outputs
- Need test fixtures for parser testing
- Tool output format changes
- Building new MCP servers (Network, Web, Vulnerability, etc.)

**Key Capabilities**:
- Generates XML parsers (nmap, nikto, OpenVAS)
- Generates JSON parsers (masscan, nuclei, ZAP)
- Generates text parsers (gobuster, searchsploit)
- Creates Pydantic models for structured data
- Generates comprehensive test suites
- Creates realistic test fixtures

**Example Usage**:
```
User: "I need to parse nmap XML output"
Claude: [Uses parser-generator to create nmap XML parser with Pydantic models and tests]

User: "My gobuster parser crashes on special characters"
Claude: [Uses parser-generator to create error-resilient gobuster parser]
```

**Deliverables**:
- Complete parser implementation
- Pydantic validation models
- pytest test suite (happy path, edge cases, errors)
- Test fixtures (mock outputs)
- Integration examples

---

### 3. Pydantic AI Agent Architect (`pydantic-agent-builder`)

**Purpose**: Builds specialized agents following Pydantic AI framework best practices.

**Use When**:
- Implementing missing specialized agents (Vulnerability, Forensic, Social, Report)
- Refactoring agents to follow Pydantic AI patterns
- Creating multi-agent workflows (A2A patterns)
- Implementing adaptive learning in agents
- Integrating MCP tools into agents

**Key Capabilities**:
- Generates complete Pydantic AI agent implementations
- Creates proper tool integrations with type safety
- Implements dependency injection patterns
- Integrates ML algorithms (fuzzy logic, Q-learning, genetic algorithms)
- Designs agent state management
- Creates multi-agent orchestration patterns

**Example Usage**:
```
User: "I need to implement the Vulnerability Agent"
Claude: [Uses pydantic-agent-builder to create complete Vulnerability Agent with sqlmap/metasploit integration]

User: "How do I add learning to the Network Agent?"
Claude: [Uses pydantic-agent-builder to integrate Q-learning for adaptive tool selection]
```

**Deliverables**:
- Complete agent implementation
- Pydantic models (config, input, output, state)
- Tool functions with MCP integration
- Multi-agent coordination patterns
- ML integration code
- Testing strategy

---

### 4. Test Coverage Enforcer (`coverage-enforcer`)

**Purpose**: Ensures 80%+ test coverage with comprehensive, security-focused tests.

**Use When**:
- Adding new code without tests
- Coverage drops below 80%
- Creating PRs (validate coverage)
- Implementing security-critical features
- Need security-focused test cases

**Key Capabilities**:
- Analyzes coverage gaps using pytest-cov
- Generates pytest test cases
- Creates mocks for subprocess calls and MCP clients
- Generates security test cases (injection, validation)
- Creates async tests for MCP tools
- Generates fixtures and test data

**Example Usage**:
```
User: "My PR failed CI because coverage is 75%"
Claude: [Uses coverage-enforcer to identify gaps and generate missing tests]

User: "I added input validation but no tests for injection attacks"
Claude: [Uses coverage-enforcer to generate security test cases]
```

**Deliverables**:
- Coverage analysis report
- Prioritized test generation plan
- Complete test implementations
- Fixture definitions
- Coverage improvement estimate

---

### 5. Security Documentation Generator (`security-docs-generator`)

**Purpose**: Generates professional security documentation, reports, and ethical guidelines.

**Use When**:
- Adding new security tools to MCP servers
- Completing security assessments (need reports)
- Creating API documentation for MCP tools
- Need legal disclaimers and ethical guidelines
- Documenting security findings

**Key Capabilities**:
- Generates MCP tool documentation with examples
- Creates professional penetration testing reports
- Formats security findings with CVSS scores
- Generates ethical use guidelines
- Creates API reference documentation
- Ensures legal compliance

**Example Usage**:
```
User: "I added sqlmap integration"
Claude: [Uses security-docs-generator to create tool docs with ethical use guidelines]

User: "Finished all scans, need a report"
Claude: [Uses security-docs-generator to create professional pentest report]
```

**Deliverables**:
- MCP tool documentation
- Penetration testing reports
- Security findings with remediation
- Ethical use guidelines
- API documentation
- Legal disclaimers

---

## Agent Priority Recommendations

### Immediate Implementation (Sprint 0)

**Priority 1: MCP Security Validator**
- **Why**: Prevents catastrophic command injection vulnerabilities
- **Impact**: Critical for secure tool integration
- **Use**: Every MCP tool implementation

**Priority 2: Parser Generator**
- **Why**: Unblocks development of 4 missing MCP servers
- **Impact**: Accelerates tool integration
- **Use**: Network, Web, Vulnerability, Forensic, Social servers

**Priority 3: Pydantic Agent Builder**
- **Why**: Accelerates Sprint 0 agent implementation
- **Impact**: Implements missing specialized agents
- **Use**: Vulnerability, Forensic, Social, Report agents

### Secondary Implementation

**Priority 4: Test Coverage Enforcer**
- **Why**: Maintains 80% coverage requirement
- **Impact**: Quality gate for all code
- **Use**: Every feature implementation

**Priority 5: Security Documentation Generator**
- **Why**: Professional documentation and legal compliance
- **Impact**: User adoption and legal protection
- **Use**: Every tool, every assessment

---

## Agent Workflow Integration

### Typical Development Flow

1. **Design Phase**:
   - Use `pydantic-agent-builder` to design agent architecture
   - Use `parser-generator` to plan tool output handling

2. **Implementation Phase**:
   - Use `mcp-security-validator` to ensure secure coding
   - Use `parser-generator` to create parsers
   - Use `pydantic-agent-builder` to implement agents

3. **Testing Phase**:
   - Use `coverage-enforcer` to achieve 80%+ coverage
   - Use `mcp-security-validator` for security testing

4. **Documentation Phase**:
   - Use `security-docs-generator` for tool documentation
   - Use `security-docs-generator` for ethical guidelines

5. **Release Phase**:
   - Use `mcp-security-validator` for final security review
   - Use `security-docs-generator` for release notes

### Example: Adding New MCP Tool

```
Step 1: Implementation
User: "I want to add metasploit integration to the vulnerability server"

Step 2: Security Validation
Claude: [Uses mcp-security-validator to review metasploit integration security]

Step 3: Parser Creation
Claude: [Uses parser-generator to create metasploit output parser with tests]

Step 4: Test Coverage
Claude: [Uses coverage-enforcer to ensure 80%+ test coverage]

Step 5: Documentation
Claude: [Uses security-docs-generator to create metasploit tool documentation]
```

---

## Agent Configuration

All agents are configured in `.claude/agents/` directory:

```
.claude/
└── agents/
    ├── mcp-security-validator.md
    ├── parser-generator.md
    ├── pydantic-agent-builder.md
    ├── coverage-enforcer.md
    └── security-docs-generator.md
```

Each agent configuration includes:
- **name**: Agent identifier
- **description**: When to use (with examples)
- **tools**: Available Claude Code tools
- **model**: LLM model (haiku/sonnet/opus)
- **System Prompt**: Complete agent instructions

---

## Best Practices

### When to Use Agents

**Use agents for**:
- Complex, repetitive tasks
- Specialized domain expertise
- Quality enforcement (security, coverage)
- Documentation generation
- Multi-step workflows

**Don't use agents for**:
- Simple file edits
- One-off commands
- Basic questions
- Tasks you can do directly

### Agent Invocation

Agents are invoked via the Task tool:
```
Claude: "I'll use the mcp-security-validator agent to review your code."
<Task tool call to mcp-security-validator agent>
```

### Agent Results

- Agents run autonomously and return results
- Results include analysis, generated code, documentation
- You can then act on agent recommendations

---

## Security Considerations

### Agent Safety

All agents are designed with security in mind:
- **Input Validation**: Agents validate all inputs
- **Secure Coding**: Follow security best practices
- **No Destructive Actions**: Agents don't delete or modify without confirmation
- **Audit Trail**: All actions are logged

### Responsible Use

- **Authorized Only**: Use agents for authorized security testing only
- **Code Review**: Always review agent-generated code before deployment
- **Test Generated Code**: Test all generated code thoroughly
- **Legal Compliance**: Ensure agents are used within legal boundaries

---

## Troubleshooting

### Agent Not Found

If an agent is not available:
1. Check `.claude/agents/` directory exists
2. Verify agent `.md` file exists
3. Check agent YAML frontmatter is valid
4. Restart Claude Code if necessary

### Agent Errors

If an agent produces errors:
1. Review the agent prompt for clarity
2. Check if required files/context are available
3. Verify agent has necessary tools enabled
4. Review agent output for specific error messages

### Agent Performance

If an agent is slow:
1. Consider using `haiku` model for simpler tasks
2. Reduce scope of agent request
3. Break complex tasks into smaller steps
4. Use multiple agents in parallel when possible

---

## Contributing

### Adding New Agents

To add a new specialized agent:

1. **Identify Need**: What recurring task needs automation?
2. **Use agent-creator**: Let the agent-creator design the new agent
3. **Create Config**: Add `.md` file to `.claude/agents/`
4. **Test**: Validate the agent works as expected
5. **Document**: Update this file with agent details

### Improving Existing Agents

To improve an agent:

1. **Edit Config**: Modify `.claude/agents/<agent-name>.md`
2. **Update System Prompt**: Refine agent instructions
3. **Add Examples**: Add more usage examples
4. **Test**: Verify improvements work
5. **Document**: Update this file if needed

---

## Additional Resources

- **Pydantic AI Docs**: `CONTEXT.MD` (Pydantic AI reference)
- **Repository Guidelines**: `AGENTS.md` (development guidelines)
- **Security Guidelines**: `SECURITY.md`, `SECURITY_IMPLEMENTATION.md`
- **Testing Guidelines**: `pyproject.toml` (pytest configuration)

---

## Agent Metrics

Track agent effectiveness:

| Agent | Use Cases | Time Saved | Quality Impact |
|-------|-----------|------------|----------------|
| mcp-security-validator | Security reviews | ~2 hours/review | Critical vulnerabilities prevented |
| parser-generator | Parser creation | ~3 hours/parser | Robust error handling |
| pydantic-agent-builder | Agent implementation | ~6 hours/agent | Framework compliance |
| coverage-enforcer | Test generation | ~2 hours/module | 80%+ coverage maintained |
| security-docs-generator | Documentation | ~4 hours/report | Professional quality |

**Total Estimated Time Savings**: ~17+ hours per development cycle

---

**Last Updated**: 2024-11-13
**Version**: 1.0.0
**Maintainer**: Kali Agents Development Team
