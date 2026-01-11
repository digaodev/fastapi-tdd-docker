"""Test suite for fastapi-tdd-docker.

Test Organization:
- unit_*.py: Pure unit tests (all dependencies mocked, no I/O)
- integration_*.py: Integration tests (database, API, external services)

Running Tests:
- pytest tests/              # Run all tests
- pytest tests/unit_*.py     # Run only unit tests
- pytest tests/integration_*.py  # Run only integration tests
- pytest -m unit            # Run tests marked with @pytest.mark.unit
- pytest -m integration     # Run tests marked with @pytest.mark.integration
"""
