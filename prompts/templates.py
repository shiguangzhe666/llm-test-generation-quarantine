"""
Prompt templates for LLM test generation.

These templates are designed for the feasibility study phase.
They will be frozen before full experiments (Phase 3, G3 gate).
"""

# =============================================================================
# Template v0.1 - Basic unit test generation (Python / pytest)
# =============================================================================

BASIC_PYTEST_TEMPLATE = """You are a Python testing expert. Generate unit tests for the following Python code using pytest.

## Requirements
- Write thorough pytest test functions that test different scenarios
- Include edge cases, boundary conditions, and error handling
- Use descriptive test function names (test_<scenario>)
- Each test should have clear, specific assertions
- Do NOT use any external services or network calls
- Do NOT use sleep() or time-dependent assertions
- Mock any non-deterministic dependencies (random, datetime, uuid, etc.)
- Use pytest fixtures where appropriate

## Code Under Test

File: {file_path}

```python
{source_code}
```

{additional_context}

## Output

Write only the test code. Start with necessary imports.
"""

# =============================================================================
# Template v0.2 - With class/module context
# =============================================================================

CONTEXT_AWARE_TEMPLATE = """You are a Python testing expert. Generate unit tests for the target function/class.

## Target Code

File: {file_path}
Function/Class: {target_name}

```python
{source_code}
```

## Dependencies and Imports Used

```python
{imports}
```

## Related Code (for context)

```python
{related_code}
```

## Requirements
- Write pytest test functions covering:
  1. Normal/happy path scenarios
  2. Edge cases and boundary values
  3. Error conditions and exception handling
  4. Different input types if applicable
- Use specific, meaningful assertions (not just assertNotNone)
- Mock external dependencies using unittest.mock or pytest-mock
- Do NOT rely on file system, network, or time-dependent behavior
- Ensure tests are deterministic and repeatable

## Output

Write only the test code. Include all necessary imports.
"""

# =============================================================================
# Template v0.3 - Stability-aware (for comparison experiments)
# =============================================================================

STABILITY_AWARE_TEMPLATE = """You are a Python testing expert focused on writing stable, deterministic tests.

## Code Under Test

File: {file_path}

```python
{source_code}
```

## IMPORTANT Stability Requirements
- Always mock `datetime.now()`, `time.time()`, and similar time functions
- Always seed random number generators or mock `random` module
- Never assert on dictionary key ordering or set iteration order
- Use `pytest.approx()` for floating-point comparisons
- Use `sorted()` or `set()` comparisons for unordered collections
- Always close file handles and clean up temporary files
- Use `tmp_path` fixture instead of hardcoded paths
- Do NOT use `sleep()` or polling-based waits
- Ensure each test is independent (no shared mutable state)

## Output

Write only the test code. Include all necessary imports.
"""

# =============================================================================
# Metadata for experiment tracking
# =============================================================================

TEMPLATE_REGISTRY = {
    "basic_v0.1": {
        "template": BASIC_PYTEST_TEMPLATE,
        "description": "Basic pytest generation without stability constraints",
        "version": "0.1",
        "stability_constraints": False,
    },
    "context_v0.2": {
        "template": CONTEXT_AWARE_TEMPLATE,
        "description": "Context-aware generation with imports and related code",
        "version": "0.2",
        "stability_constraints": False,
    },
    "stable_v0.3": {
        "template": STABILITY_AWARE_TEMPLATE,
        "description": "Stability-aware generation with explicit determinism rules",
        "version": "0.3",
        "stability_constraints": True,
    },
}
