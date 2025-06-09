#!/bin/bash
echo "=== RAG_Scraper Development Environment Validation ==="

echo "1. Checking Python version..."
python3 --version

echo "2. Checking virtual environment..."
which python
which pip

echo "3. Checking Git status..."
git status

echo "4. Checking installed packages..."
pip list | grep -E "(flask|pytest|requests|beautifulsoup4)"

echo "5. Running setup tests..."
pytest tests/test_setup.py -v

echo "6. Checking test coverage capability..."
pytest --cov=src tests/test_setup.py --cov-report=term-missing

echo "8. Checking Claude Code installation..."
claude --version

echo "9. Checking project initialization readiness..."
if [ -f "CLAUDE.md" ]; then
    echo "✓ CLAUDE.md project file exists"
    echo "✓ Claude Code project initialization previously completed"
else
    echo "ℹ CLAUDE.md not found - run 'claude' then '/init' after validation"
    echo "ℹ This is normal for first-time setup"
fi

echo "=== Setup validation complete ==="
echo "Ready for Sprint 1 development with Claude Code TDD workflow"
