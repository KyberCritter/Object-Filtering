# (c) 2025 Scott Ratchford
# This file is licensed under the MIT License. See LICENSE.txt for details.

#!/usr/bin/env python3
import json
import sys
from object_filtering.object_filtering import (
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

def explain_expression(expr: LogicalExpression) -> str:
    """Recursively convert a logical expression into a natural-language phrase.

    Args:
        expr (LogicalExpression): The LogicalExpression to explain.

    Raises:
        TypeError: If the type of expr is unsupported.

    Returns:
        str: An English-language description of expr.
    """
    # Boolean literals
    if isinstance(expr, bool):
        return "always true" if expr else "always false"
    
    # Rule objects or dicts
    if isinstance(expr, (Rule, dict)) and set(expr.keys()).issuperset({"criterion", "operator", "comparison_value"}):
        criterion = expr["criterion"]
        op = expr["operator"]
        val = expr["comparison_value"]
        params = expr.get("parameters", [])
        param_str = ""
        if params and len(params) > 0:
            if len(params) == 1:
                param_str = f" with parameter {params[0]}"
            else:
                param_str = f" with parameters {", ".join(map(str, params[:-1]))} and {params[-1]}"
            return f"the result of calling {criterion}{param_str} {OPERATOR_MAP[op]} {val}"
        return f"{criterion} {OPERATOR_MAP[op]} {val}"
    
    # GroupExpression objects or dicts
    if isinstance(expr, (GroupExpression, dict)) and "logical_operator" in expr:
        conj = expr["logical_operator"]
        parts = [explain_expression(sub) for sub in expr["logical_expressions"]]
        return f" {conj+' '}".join(parts)
    
    # ConditionalExpression objects or dicts
    if isinstance(expr, (ConditionalExpression, dict)) and set(expr.keys()).issuperset({"if", "then", "else"}):
        cond = explain_expression(expr["if"])
        then = explain_expression(expr["then"])
        el = explain_expression(expr["else"])
        return f"If {cond}, then {then}; otherwise, {el}"
    
    raise TypeError(f"Unsupported expression type: {expr}")

def explain_filter(obj_filter: ObjectFilter) -> str:
    """Generate a full English explanation of an ObjectFilter.

    Args:
        obj_filter (ObjectFilter): The ObjectFilter to explain.

    Returns:
        str: An English-language explanation of obj_filter.
    """
    name = obj_filter.get("name", "(unnamed)")
    desc = obj_filter.get("description", "")
    types = obj_filter.get("object_types", [])
    expr = obj_filter.get("logical_expression", True)
    
    header = f"Filter '{name}': {desc}".strip()
    applies = f"This filter applies to object types: {', '.join(types)}."
    criteria = explain_expression(expr)

    return f"{header}\n{applies}\nCriteria: {criteria}."
