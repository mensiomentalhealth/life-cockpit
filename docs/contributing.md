# Contributing to Life Cockpit

Thank you for your interest in contributing to Life Cockpit! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome contributions in the following areas:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new functionality
- **📝 Documentation**: Improve guides, examples, and API docs
- **💻 Code Contributions**: Submit pull requests with improvements
- **🧪 Testing**: Add tests or improve test coverage
- **🔧 Infrastructure**: Help with CI/CD, deployment, or tooling

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** following our guidelines
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/life-cockpit.git
cd life-cockpit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available

# Set up pre-commit hooks
pre-commit install
```

### Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
# Add your Microsoft 365 and Dataverse credentials
```

## 📋 Code Style Guidelines

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 88 characters (Black formatter default)
- **Indentation**: 4 spaces (no tabs)
- **String Quotes**: Double quotes for docstrings, single quotes for strings
- **Import Order**: Standard library, third-party, local imports

### Code Formatting

We use automated tools for consistent formatting:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code style with flake8
flake8 .
```

### Type Hints

- Use type hints for all function parameters and return values
- Use `Optional[T]` for nullable types
- Use `Union[T1, T2]` for multiple types
- Import types from `typing` module

```python
from typing import Optional, List, Dict, Any

def process_data(data: List[Dict[str, Any]]) -> Optional[str]:
    """Process the input data and return a result."""
    pass
```

### Documentation

#### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def authenticate_user(client_id: str, client_secret: str) -> bool:
    """Authenticate a user with Microsoft Graph API.
    
    Args:
        client_id: The Azure application client ID
        client_secret: The Azure application client secret
        
    Returns:
        True if authentication successful, False otherwise
        
    Raises:
        AuthenticationError: If authentication fails
    """
    pass
```

#### Comments

- Write clear, concise comments explaining "why" not "what"
- Use comments for complex business logic
- Avoid obvious comments that just repeat the code

### Naming Conventions

- **Functions and Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Modules**: `snake_case`
- **Packages**: `snake_case`

## 🧪 Testing Guidelines

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test module interactions
- **End-to-End Tests**: Test complete workflows

### Test Naming

Use descriptive test names that explain the scenario:

```python
def test_authenticate_user_with_valid_credentials_returns_true():
    """Test that valid credentials result in successful authentication."""
    pass

def test_authenticate_user_with_invalid_credentials_raises_error():
    """Test that invalid credentials raise AuthenticationError."""
    pass
```

### Test Coverage

- Aim for >90% code coverage
- Focus on critical business logic
- Test error conditions and edge cases
- Mock external dependencies

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure tests pass** locally
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Check code style** with formatting tools
5. **Update CHANGELOG.md** with your changes

### Pull Request Template

Use this template when creating pull requests:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG updated

## Screenshots (if applicable)
Add screenshots for UI changes
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and style checks
2. **Code Review**: At least one maintainer reviews the PR
3. **Discussion**: Address any feedback or questions
4. **Approval**: PR is approved and merged

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear and concise description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g. Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- Life Cockpit Version: [e.g. 1.0.0]

## Additional Context
Add any other context, logs, or screenshots
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Problem Statement
Clear description of the problem this feature would solve

## Proposed Solution
Description of the proposed feature

## Alternative Solutions
Any alternative solutions you've considered

## Additional Context
Add any other context, use cases, or examples
```

## 📝 Documentation Contributions

### Documentation Standards

- **Clear and Concise**: Write for the target audience
- **Examples**: Include practical examples
- **Code Blocks**: Use syntax highlighting
- **Links**: Link to related documentation
- **Images**: Include diagrams when helpful

### Documentation Structure

- **README.md**: Project overview and quick start
- **docs/**: Detailed documentation
- **examples/**: Code examples and tutorials
- **api/**: API reference documentation

## 🔒 Security

### Security Guidelines

- **Never commit secrets** (API keys, passwords, etc.)
- **Use environment variables** for configuration
- **Validate all inputs** to prevent injection attacks
- **Follow OWASP guidelines** for web security
- **Report security issues** privately to maintainers

### Security Issues

For security-related issues, please email security@mensiomentalhealth.com instead of creating a public issue.

## 🏷️ Version Control

### Branch Naming

- **Feature branches**: `feature/description`
- **Bug fixes**: `fix/description`
- **Documentation**: `docs/description`
- **Hotfixes**: `hotfix/description`

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(auth): add OAuth2 authentication support
fix(dataverse): resolve connection timeout issue
docs(api): update Graph API documentation
```

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** and considerate of others
- **Be collaborative** and open to feedback
- **Be constructive** in criticism and suggestions
- **Be inclusive** and welcoming to new contributors

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions
- **Email**: For security issues or private matters

## 🎯 Getting Help

### Resources

- **Documentation**: Check the docs/ directory
- **Examples**: Look at examples/ directory
- **Issues**: Search existing issues for similar problems
- **Discussions**: Ask questions in GitHub Discussions

### Contact

- **Maintainers**: @mensiomentalhealth
- **Email**: ben@mensiomentalhealth.com
- **Website**: https://mensiomentalhealth.com

## 🙏 Recognition

Contributors will be recognized in:

- **README.md**: List of contributors
- **CHANGELOG.md**: Credit for significant contributions
- **Release Notes**: Acknowledgment of contributions

Thank you for contributing to Life Cockpit! Your contributions help make automation more accessible and powerful for everyone.
