# (c) 2026 Scott Ratchford
# This file is licensed under the MIT License. See LICENSE.txt for details.

from ..object_filtering import (
    ObjectFilter, Rule, GroupExpression, ConditionalExpression,
    LogicalExpression,
)


# Map operators to English phrases
OPERATOR_MAP = {
    "<": "is less than",
    "<=": "is less than or equal to",
    "==": "equals",
    "!=": "does not equal",
    ">=": "is greater than or equal to",
    ">": "is greater than"
}

def explain_expression(expr: LogicalExpression, depth: int = 0) -> str:
    """Recursively convert a logical expression into an indented, multi-line
    English-language description.

    Args:
        expr (LogicalExpression): The LogicalExpression to explain.
        depth (int, optional): Depth of the expression within a larger
            expression. Defaults to 0.

    Raises:
        TypeError: If the type of expr is not LogicalExpression.

    Returns:
        str: A description of expr.
    """
    indent = '    ' * depth

    # Boolean literals
    if isinstance(expr, bool):
        text = "This condition is always true." if expr else "This condition is always false."
        return f"{indent}{text}"

    # Rule objects
    if isinstance(expr, Rule):
        params = expr.get("parameters", [])
        if params:
            if len(params) == 1:
                param_str = f" with parameter {params[0]}"
            else:
                joined = ", ".join(map(str, params[:-1]))
                param_str = f" with parameters {joined} and {params[-1]}"
            text = f"The result of calling {expr.criterion}{param_str} {OPERATOR_MAP[expr.operator]} {expr.comparison_value}."
        else:
            text = f"{expr.criterion} {OPERATOR_MAP[expr.operator]} {expr.comparison_value}."
        return f"{indent}{text}"

    # GroupExpression objects
    if isinstance(expr, GroupExpression):
        parts = expr.get("logical_expressions", [])
        if expr.logical_operator == "and":
            header = "All of the following conditions must be met:"
        else:
            header = "At least one of the following conditions must be met:"
        lines = [f"{indent}{header}"]
        for sub in parts:
            sub_text = explain_expression(sub, depth + 1).strip()
            lines.append(f"{indent}    - {sub_text}")
        return "\n".join(lines)

    # ConditionalExpression objects
    if isinstance(expr, ConditionalExpression):
        cond_lines = explain_expression(expr._if, depth + 1).strip()
        then_lines = explain_expression(expr._then, depth + 1).strip()
        else_lines = explain_expression(expr._else, depth + 1).strip()
        lines = [
            f"{indent}If the following condition holds:",
            f"{indent}    - {cond_lines}",
            f"{indent}Then:",
            f"{indent}    - {then_lines}",
            f"{indent}Otherwise:",
            f"{indent}    - {else_lines}"
        ]
        return "\n".join(lines)

    raise TypeError(f"Unsupported expression type: {expr}")

def explain_filter(object_filter: ObjectFilter) -> str:
    """Generate an English explanation of the entire ObjectFilter.

    Args:
        obj_filter (ObjectFilter): The ObjectFilter to describe.

    Returns:
        str: An English-language description of the ObjectFilter.
    """
    header = f"Filter \"{object_filter.name}\": {object_filter.description}".strip()
    if len(object_filter.object_types) > 1:
        type_list = ", ".join(object_filter.object_types[:-1]) + f", and {object_filter.object_types[-1]}"
        applies = f"This filter applies to objects of types: {type_list}."
    else:
        applies = f"This filter applies to objects of type: {object_filter.object_types[0]}."

    criteria = explain_expression(object_filter.logical_expression)
    return f"{header}\n{applies}\n{criteria}"
