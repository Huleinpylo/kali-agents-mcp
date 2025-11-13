# Contributing to Kali Agents MCP

? **Thank you for your interest in contributing to Kali Agents MCP!** This project aims to revolutionize cybersecurity automation while maintaining the highest security and ethical standards.

- Start with `AGENTS.md` for a concise repository overview (structure, tooling, expectations).
- Keep `CONTEXT.MD` handy; it lists the Pydantic AI documentation that powers our agent architecture.
- Review `memory.md` at the start of every session to learn about outstanding failures, priorities, and recent fixes.

## ? Project Mission

**"Kali Agents at Your Service"** - Transform Kali Linux from a toolbox into an intelligent cybersecurity assistant that orchestrates complex security workflows automatically.

## ?? Security-First Approach

Before contributing, please understand that this project:
- Handles powerful cybersecurity tools
- Requires ethical usage guidelines
- Must maintain strict security standards
- Follows responsible disclosure practices

## ? How to Contribute

### ? Areas Where We Need Help

#### ? **AI/ML Enhancement**
- Improve fuzzy logic algorithms
- Enhance genetic algorithm optimization
- Expand Q-learning capabilities
- Add new pattern recognition features

#### ? **Tool Integration**
- Add new Kali Linux tool wrappers
- Improve parsing and result extraction
- Create specialized MCP servers
- Enhance tool orchestration

#### ? **Architecture Improvement**
- Optimize agent communication
- Enhance performance monitoring
- Improve error handling
- Add scalability features

#### ? **Documentation & Training**
- User guides and tutorials
- API documentation
- Security best practices
- Educational content

#### ? **Testing & Quality Assurance**
- Unit and integration tests
- Security testing
- Performance benchmarks
- Compliance validation

### ? Before You Start

1. **Read the Security Policy**: Understand our [SECURITY.md](SECURITY.md) thoroughly
2. **Check Issues**: Look for existing issues you can help with
3. **Discuss First**: For major changes, open an issue to discuss the approach
4. **Fork & Clone**: Create your own fork of the repository

### ? Development Workflow

#### 1. **Setup Development Environment**
```bash
# Clone your fork
git clone https://github.com/your-username/kali-agents-mcp.git
cd kali-agents-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### 2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

#### 3. **Development Guidelines**

##### ? **Code Style**
- Follow PEP 8 for Python code
- Use type hints for all functions
- Add comprehensive docstrings
- Include security considerations in comments

##### ? **Security Requirements**
- **Input Validation**: Validate all user inputs
- **Authorization Checks**: Implement proper access controls
- **Logging**: Add audit trails for security-relevant actions
- **Error Handling**: Don't expose sensitive information in errors

##### ? **Documentation**
- Update relevant documentation
- Add inline comments for complex logic
- Include security considerations
- Provide usage examples

#### 4. **Testing Requirements**
```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run security tests
python -m pytest tests/security/

# Check code coverage
python -m pytest --cov=src/ --cov-report=html
```

#### 5. **Commit Guidelines**
```bash
# Use conventional commits
git commit -m "feat: add new network scanning capabilities"
git commit -m "fix: resolve SQL injection vulnerability"
git commit -m "docs: update security guidelines"
git commit -m "test: add integration tests for web agent"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `security`: Security improvements

#### 6. **Submit Pull Request**

##### ? **PR Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] No sensitive data exposed
- [ ] Backward compatibility maintained

##### ? **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Security improvement
- [ ] Documentation update
- [ ] Performance improvement

## Security Considerations
- How does this change affect security?
- Are there any new attack vectors?
- Have authorization checks been added?

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments added
- [ ] Documentation updated
- [ ] README updated if needed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No sensitive data exposed
- [ ] Backward compatibility maintained
```

## ? Security Guidelines for Contributors

### ?? **Sensitive Information**
- **Never commit**: API keys, passwords, or credentials
- **Use environment variables**: For configuration secrets
- **Sanitize logs**: Don't log sensitive data
- **Review carefully**: Check for accidental data exposure

### ?? **Code Security**
- **Input validation**: Always validate and sanitize inputs
- **SQL injection**: Use parameterized queries
- **Command injection**: Escape shell commands properly
- **Path traversal**: Validate file paths
- **Authentication**: Implement proper auth checks

### ? **Vulnerability Reporting**
If you discover a security vulnerability while contributing:
1. **Do NOT create a public issue**
2. Email details to the security team
3. Allow reasonable time for fixes
4. Follow responsible disclosure practices

## ? Code Review Process

### ? **Review Requirements**
- All PRs require at least one approval
- Security-related changes require security team review
- Major architectural changes require architect approval
- Breaking changes require maintainer approval

### ? **Review Criteria**
- **Functionality**: Does it work as intended?
- **Security**: Are there security implications?
- **Performance**: Does it impact performance?
- **Maintainability**: Is the code clean and well-documented?
- **Testing**: Are there adequate tests?

## ? Learning Resources

### ? **Technical Knowledge**
- [FastMCP Documentation](https://github.com/pydantic/fastmcp)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [Kali Linux Tools](https://www.kali.org/tools/)
- [Python Security Best Practices](https://python.org/dev/security/)

### ? **Security Education**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Ethical Hacking Guidelines](https://www.eccouncil.org/ethical-hacking/)

## ? Recognition

### ? **Contributor Levels**
- **New Contributor**: First contribution
- **Regular Contributor**: Multiple contributions
- **Core Contributor**: Significant ongoing contributions
- **Maintainer**: Repository maintenance privileges

### ?? **Recognition Methods**
- Contributors list in README
- GitHub contributor graphs
- Special recognition for security improvements
- Conference speaking opportunities

## ? Getting Help

### ? **Communication Channels**
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions
- **Security Email**: For security-related matters
- **Pull Request Comments**: For code-specific questions

### ? **Mentorship**
New contributors can request mentorship from experienced contributors. We provide:
- Code review guidance
- Architecture explanations
- Security best practices training
- Career development advice

## ? Code of Conduct

### ? **Our Standards**
- Be respectful and inclusive
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Show empathy towards other contributors
- Take responsibility for mistakes

### ? **Unacceptable Behavior**
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Publishing private information
- Malicious use of project tools

## ? Legal Considerations

### ?? **Contributor License Agreement**
By contributing, you agree that:
- Your contributions are your original work
- You have the right to submit the contributions
- Your contributions will be licensed under GPL-3.0
- You understand the ethical usage requirements

### ? **International Compliance**
Contributors must ensure their contributions comply with:
- Local export control laws
- Cybersecurity regulations
- Data protection requirements
- Professional ethics standards

---

## ? Thank You!

Your contributions help make cybersecurity more accessible and effective for security professionals worldwide. Together, we're building the future of intelligent security automation!

**Questions?** Open an issue or reach out to the maintainers. We're here to help! ?

---
*Last updated: 2025-06-13*
