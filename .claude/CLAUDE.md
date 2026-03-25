# Project Guidelines

## Running Code

Always use `uv run` to execute Python code and tests (e.g., `uv run python -m pytest`). Never use bare `python` or `py`.

## Code Style

### Strings

- Use double quotes for regular strings.
- Use single quotes only for forward-reference type hint strings (e.g., `'list[LogicalExpression]'` not `"list[LogicalExpression]"`) and nested dict access inside f-strings.
- Use f-strings with double-quotes instead of string addition.

### Formatting

- Format Python dict literals with JSON-style pretty-printing: one key-value pair per line, 4-space indentation. Opening brace on the assignment line, each key on its own indented line, closing brace on its own line.
- Multi-line function parameters: each on its own line, indented 2 levels (8 spaces) from the `def`.

### Docstrings

- Use Google-style docstrings with `Args:`, `Raises:`, `Returns:` sections.
- Include type annotations in parentheses in the `Args:` section (e.g., `param (type): Description.`).

### Imports

- Order: stdlib, third-party, local (with blank lines between groups).

### Type Hints

- Use modern union syntax (`int | float`, not `Union[int, float]`).
- Always annotate return types, including `-> None`.

### File Headers

- `# (c) YEAR Author Name`
- `# This file is licensed under the MIT License. See LICENSE.txt for details.`

### Tests

- Use `unittest.TestCase` subclasses named `Test[FeatureName]`.
- One assertion focus per test method.
