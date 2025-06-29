# Contributing to Ageny Online

Thank you for your interest in contributing to Ageny Online! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug Reports**: Report bugs and issues
- 💡 **Feature Requests**: Suggest new features
- 📝 **Documentation**: Improve or add documentation
- 🔧 **Code**: Submit code improvements
- 🧪 **Tests**: Add or improve tests
- 🌐 **Translations**: Help with internationalization

### Before You Start

1. **Check existing issues** to avoid duplicates
2. **Read the documentation** to understand the project
3. **Set up your development environment** (see below)
4. **Follow the coding standards** outlined in this guide

## 🚀 Development Setup

### Prerequisites

- Python 3.12+
- Git
- Docker & Docker Compose (optional)
- Poetry (recommended) or pip

### Local Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/ageny_online.git
   cd ageny_online
   ```

2. **Set up virtual environment**
   ```bash
   # Using Poetry (recommended)
   poetry install
   poetry shell
   
   # Or using venv
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env.online
   # Edit .env.online with your API keys
   ```

4. **Run the application**
   ```bash
   # Using Poetry
   poetry run uvicorn src.backend.api.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or directly
   uvicorn src.backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📝 Code Standards

### Python Code Style

We follow PEP 8 and use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **ruff**: Fast Python linter

### Pre-commit Hooks

Install pre-commit hooks to automatically format and check your code:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Run linting with ruff
ruff check src/ tests/
ruff format src/ tests/
```

### Type Hints

All public functions and methods must have type hints:

```python
from typing import List, Optional, Dict, Any

def process_data(data: List[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process the input data according to configuration.
    
    Args:
        data: List of data dictionaries to process
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing processed results
    """
    # Implementation here
    pass
```

### Docstrings

Use Google-style docstrings for all public classes and methods:

```python
class DataProcessor:
    """Processes data using various AI providers.
    
    This class handles the processing of data through different AI providers
    with automatic fallback and error handling.
    
    Attributes:
        providers: List of available AI providers
        config: Configuration dictionary
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the DataProcessor.
        
        Args:
            config: Configuration dictionary containing provider settings
        """
        self.config = config
        self.providers = self._load_providers()
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run specific test file
pytest tests/unit/test_config.py

# Run with verbose output
pytest -v
```

### Writing Tests

#### Test Structure

```python
import pytest
from unittest.mock import patch, AsyncMock
from src.backend.core.llm_providers.openai_client import OpenAIProvider

class TestOpenAIProvider:
    """Test cases for OpenAI provider."""
    
    def test_initialization(self):
        """Test provider initialization."""
        provider = OpenAIProvider("test-key")
        assert provider.api_key == "test-key"
        assert provider.default_model == "gpt-4o-mini"
    
    @pytest.mark.asyncio
    async def test_chat_completion(self):
        """Test chat completion functionality."""
        with patch('openai.AsyncOpenAI') as mock_client:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Hello, world!"
            mock_client.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            provider = OpenAIProvider("test-key")
            result = await provider.chat_completion("Hello")
            
            assert result["content"] == "Hello, world!"
```

#### Test Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Mock external dependencies** to avoid network calls
3. **Test both success and failure cases**
4. **Use fixtures** for common test data
5. **Maintain test isolation** - each test should be independent
6. **Aim for >90% code coverage**

## 🔄 Development Workflow

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write your code following the coding standards
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Your Changes

Use conventional commit messages:

```bash
# Format: type(scope): description
git commit -m "feat(api): add new chat endpoint"
git commit -m "fix(ocr): resolve image processing error"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(providers): add OpenAI provider tests"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 4. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/amazing-feature

# Create Pull Request on GitHub
```

## 📋 Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Code coverage maintained or improved

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new functionality

## Related Issues
Closes #(issue number)
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the bug
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, etc.)
5. **Error messages** and stack traces
6. **Screenshots** if applicable

## 💡 Feature Requests

When suggesting features:

1. **Clear description** of the feature
2. **Use case** and benefits
3. **Implementation suggestions** if possible
4. **Mockups** or examples if applicable

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the project's coding standards
- Be patient with newcomers

### Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for general questions
- Be clear and specific in your communications
- Use English for all project communications

## 📞 Getting Help

If you need help:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Create a new issue** with clear details
4. **Join discussions** in GitHub Discussions
5. **Contact maintainers** for urgent issues

## 🙏 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **CHANGELOG.md** for significant contributions
- **GitHub contributors** page
- **Release notes** for major releases

---

Thank you for contributing to Ageny Online! Your contributions help make this project better for everyone. 🚀 