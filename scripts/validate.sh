#!/usr/bin/env bash
# Comprehensive validation script - catches errors before commit
set -e

echo "🔍 Running comprehensive validation..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# 1. Test imports (catches undefined names)
echo "📦 Testing imports..."
if uv run python -c "from fastapi_tdd_docker.main import app; print('✅ All imports valid')"; then
    echo -e "${GREEN}✅ Import check passed${NC}"
else
    echo -e "${RED}❌ Import check failed - undefined names detected${NC}"
    FAILED=1
fi
echo ""

# 2. Ruff linting
echo "🔍 Running Ruff linter..."
if uv run ruff check src; then
    echo -e "${GREEN}✅ Ruff check passed${NC}"
else
    echo -e "${RED}❌ Ruff check failed${NC}"
    FAILED=1
fi
echo ""

# 3. Type checking
echo "📝 Running MyPy type checker..."
if uv run mypy src; then
    echo -e "${GREEN}✅ Type check passed${NC}"
else
    echo -e "${RED}❌ Type check failed${NC}"
    FAILED=1
fi
echo ""

# 4. Run tests
echo "🧪 Running tests..."
if uv run pytest src/fastapi_tdd_docker/tests/ -v --tb=short; then
    echo -e "${GREEN}✅ Tests passed${NC}"
else
    echo -e "${RED}❌ Tests failed${NC}"
    FAILED=1
fi
echo ""

# Summary
echo "============================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All validations passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Validation failed - please fix errors above${NC}"
    exit 1
fi
