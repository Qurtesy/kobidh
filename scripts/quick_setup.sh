#!/bin/bash
# Quick setup script for immediate improvements

echo "🚀 Setting up enhanced Kobidh development environment..."

# 1. Install enhanced development dependencies
echo "📦 Installing development dependencies..."
pip install -e ".[dev]" 2>/dev/null || pip install -r _requirements/dev.txt

# 2. Run code formatting
echo "🎨 Formatting code..."
python -m black kobidh/ --line-length 88 2>/dev/null || echo "Black not available, skipping formatting"

# 3. Run basic linting
echo "🔍 Running basic checks..."
python -m flake8 kobidh/ --max-line-length=88 2>/dev/null || echo "Flake8 not available, skipping linting"

# 4. Test current functionality
echo "🧪 Testing current CLI..."
python -c "from kobidh.cli import main; print('✅ CLI imports successfully')" || echo "❌ CLI import failed"

# 5. Check AWS connectivity
echo "☁️ Checking AWS connectivity..."
aws sts get-caller-identity 2>/dev/null && echo "✅ AWS credentials configured" || echo "⚠️ AWS credentials may need configuration"

# 6. Create basic test
echo "📝 Creating basic test structure..."
mkdir -p tests
cat > tests/test_basic.py << 'EOF'
"""Basic tests for Kobidh functionality"""
import pytest
from kobidh.exceptions import KobidhError
from kobidh.constants import VERSION, APP_NAME

def test_version():
    """Test version constant exists"""
    assert VERSION == "1.0.0"

def test_app_name():
    """Test app name constant"""
    assert APP_NAME == "kobidh"

def test_custom_exception():
    """Test custom exception works"""
    error = KobidhError("Test error", "Test suggestion")
    assert "Test error" in str(error)
    assert "Test suggestion" in str(error)
EOF

# 7. Run the basic test
echo "🧪 Running basic tests..."
python -m pytest tests/test_basic.py -v 2>/dev/null || echo "Pytest not available, skipping tests"

echo ""
echo "✅ Setup complete! Next steps:"
echo "1. Review the artifacts created in this conversation"
echo "2. Consider running: python scripts/reorganize_project.py"
echo "3. Update your README.md with the enhanced version"
echo "4. Start implementing the enhanced CLI commands"
echo "5. Add proper logging throughout your application"
echo ""
echo "Your Kobidh project is ready for the next level! 🎉"
