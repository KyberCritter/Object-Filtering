# (c) 2025 Scott Ratchford
# This file is licensed under the MIT License. See LICENSE.txt for details.

import functools
from decimal import Decimal
from inspect import getmro
from sys import getsizeof
from typing import Any, Callable, Iterable
from math import isclose

import numpy as np


ABS_TOL = Decimal(0.0001)
VALID_OPERATORS = set(["<", "<=", "==", "!=", ">=", ">"])
VALID_LOGICAL_OPERATORS = set(["and", "or"])
VALID_MULTI_VALUE_BEHAVIORS = set(["none", "add", "each_meets_criterion", "each_equal_in_object"])

class ObjectFilter(dict):
    def __init__(
            self, name: str = "", description: str = "", priority: int = 0,
            object_types: list = ["object"], logical_expression: bool | dict = True
        ) -> None:
        super().__init__()
        self["name"] = name
        self["description"] = description
        self["priority"] = priority
        self["object_types"] = object_types
        self["logical_expression"] = logical_expression

class Rule(dict):
    def __init__(
            self, criterion: str = "__class__", operator: str = "==",
            comparison_value: int | float | str | bool = "", parameters: list = [],
            multi_value_behavior: str = "none"
        ) -> None:
        super().__init__()
        self["criterion"] = criterion
        self["operator"] = operator
        self["comparison_value"] = comparison_value
        self["parameters"] = parameters
        self["multi_value_behavior"] = multi_value_behavior

class GroupExpression(dict):
    def __init__(
            self, logical_operator: str = "and", logical_expressions: list = []
        ) -> None:
        super().__init__()
        self["logical_operator"] = logical_operator
        self["logical_expressions"] = logical_expressions

class ConditionalExpression(dict):
    def __init__(
            self, if_branch: bool | dict = True, then_branch: bool | dict = True,
            else_branch: bool | dict = True
        ) -> None:
        super().__init__()
        self["if"] = if_branch
        self["then"] = then_branch
        self["else"] = else_branch

LogicalExpression = bool | Rule | ConditionalExpression | GroupExpression | ObjectFilter

def filter_criterion(func):
    """Decorator that whitelists method use for filters.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper._is_whitelisted = True
    return wrapper

class FilterError(ValueError):
    """Base class for all ObjectFilter errors.
    """
    def __init__(self, *args):
        super().__init__(*args)

"""
Helper and Sanitization Functions
"""

def type_name_matches(obj: Any, target_type_names: Iterable[str]) -> bool:
    """Evaluates whether obj is an instance of a class with a name matching target_type_name.
    If obj is an ObjectWrapper, the types of the elements of obj._obj are checked instead.

    Args:
        obj (Any): The object to check the type of.
        target_type_name (str): The __name__ of a type.

    Returns:
        bool: True if obj is an instance of a type matching target_type_name.
    """
    if isinstance(obj, ObjectWrapper) and isinstance(obj._obj, Iterable):
        for element in obj._obj:
            this_valid = False
            for cls in getmro(type(element)):
                try:
                    if cls.__name__ in target_type_names:
                        this_valid = True
                except:
                    pass
            if not this_valid:
                return False
            
        return True
    else:
        if isinstance(obj, ObjectWrapper):
            obj = obj._obj
            
        for cls in getmro(type(obj)):
            try:
                if cls.__name__ in target_type_names:
                    return True
            except:
                pass

        return False

def get_logical_expression_type(expression: bool | dict) -> str:
    """Determines the type of a logical expression based on its contents.

    Args:
        expression (bool | dict): A logical expression to evaluate.

    Raises:
        TypeError: If expression is not a bool or dict.
        ValueError: If expression is a dict but its keys do not match any logical expression.

    Returns:
        str: "boolean", "rule", "conditional_expression", "group_expression", or "filter"
    """
    if isinstance(expression, bool):
        return "boolean"
    elif not isinstance(expression, dict):
        raise TypeError("expression is not a bool or dict")
    key_set = set(expression.keys())
    if set(("criterion", "operator", "comparison_value", "parameters", "multi_value_behavior")).issubset(key_set):
        return "rule"
    if set(("if", "then", "else")).issubset(key_set):
        return "conditional_expression"
    if set(("logical_operator", "logical_expressions")).issubset(key_set):
        return "group_expression"
    if set(("name", "description", "priority", "object_types", "logical_expression")).issubset(key_set):
        return "filter"

    raise ValueError("expression is not a logical expression of any kind " + \
                     "(boolean, rule, group expression, conditional expression, or filter)")

def is_logical_expression_valid(expression: bool | dict, obj: Any = None) -> bool:
    """Determines whether a logical expression conforms to the format from the documentation.

    Args:
        expression (bool | dict): The logical expression (boolean, rule,
            conditional expression, or group expression) to check the validity of.
        obj (Any): The object that will be filtered. All criteria in the rules
            must be present and whitelisted for its type. Defaults to None.

    Raises:
        ValueError: If expression is not a logical expression of any kind
            (boolean, rule, group expression, conditional expression, or filter)

    Returns:
        bool: Whether the logical expression is valid.
    """
    expression_type = get_logical_expression_type(expression)
    if expression_type == "boolean":
        return True # True and False are both valid
    elif expression_type == "rule":
        return is_rule_valid(expression, obj)
    elif expression_type == "conditional_expression":
        return is_conditional_expression_valid(expression, obj)
    elif expression_type == "group_expression":
        return is_group_expression_valid(expression, obj)
    elif expression_type == "filter":
        return is_filter_valid(expression, obj)
    else:
        raise ValueError("expression is not a logical expression of any kind " + \
                        "(boolean, rule, group expression, conditional expression, or filter)")

def is_rule_valid(rule: dict, obj: Any = None) -> bool:
    """Determines whether a rule conforms to the format from the documentation.
    All methods used as criteria must be decorated with @filter_criterion.
    Raises an error if the rule is not valid.

    Args:
        rule (dict): The rule to check the validity of.
        obj (Any): The object that will be filtered.
            All criteria in the rules must be present and whitelisted for its type.
            Defaults to None.

    Returns:
        bool: Whether the rule is valid

    - Required keys and their values' data types:
        - criterion (str): The variable or method to compare against.
        - operator (str): A string representing the comparison operator to use.
            Allowed values are: `"<"`, `">"`, `"<="`, `">="`, `"=="`, or `"!="`.
        - comparison_value: The value to compare the value of the criterion with.
        - parameters (list): Passed into the method if the criterion is a method.
    """
    if get_logical_expression_type(rule) != "rule":
        raise FilterError("rule is not a rule.")
    # value types
    if not isinstance(rule["criterion"], str):
        raise FilterError("rule criterion is not a string.")
    if not isinstance(rule["operator"], str):
        raise FilterError("rule operator is not a string.")
    # no type check for comparison_value, since it varies
    if not isinstance(rule["parameters"], list):
        raise FilterError("rule parameter is not a list.")
    if not isinstance(rule["multi_value_behavior"], str):
        raise FilterError("rule multi_value_behavior is not a string.")
    
    if obj is not None:
        # value checks
        if rule["operator"].upper() not in VALID_OPERATORS:
            raise FilterError("rule operator is not a valid operator.")
        try:    # check if method exists
            method = getattr(obj, rule["criterion"])
        except:
            raise FilterError(f"method {rule['criterion']} does not exist in obj.")
        # check if method is decorated with @filter_criterion
        if not isinstance(obj, ObjectWrapper):
            if callable(method) and not hasattr(method, "_is_whitelisted"):
                raise FilterError(f"method {rule['criterion']} is not whitelisted in obj. No _is_whitelisted method.")
            if hasattr(method, "_is_whitelisted") and not method._is_whitelisted:
                raise FilterError(f"method {rule['criterion']} is not whitelisted in obj.")
            if rule["multi_value_behavior"] not in VALID_MULTI_VALUE_BEHAVIORS:
                raise FilterError(f"rule multi_value_behavior is not a valid multi_value_behavior.")

    return True

def is_conditional_expression_valid(expression: dict, obj: Any = None) -> bool:
    """Determines whether a rule conforms to the format from the documentation.
    Raises an error if the conditional expression is not valid.

    Args:
        expression (dict): The conditional expression to check the validity of.
        obj (Any): The object that will be filtered.
            All criteria in the rules must be present and whitelisted for its type.
            Defaults to None.

    Returns:
        bool: Whether the conditional expression is valid.
    
    - Required keys and their values' data types:
        - if (bool | dict): The first logical expression to evaluate
        - then (bool | dict): The logical expression to evaluate if the "if" branch evaluates to True.
        - else (bool | dict): The logical expression to evaluate if the "if" branch evaluates to False.
    """
    if get_logical_expression_type(expression) != "conditional_expression":
        raise FilterError("expression is not a conditional expression.")
    return all([is_logical_expression_valid(exp, obj) for exp in expression.values()])

def is_group_expression_valid(expression: dict, obj: Any = None) -> bool:
    """Determines whether the group expression conforms to the format from the documentation.

    Args:
        expression (dict): The group expression to check the validity of.
        obj (Any): The object that will be filtered.
            All criteria in the rules must be present and whitelisted for its type.
            Defaults to None.

    Returns:
        bool: Whether the group expression is valid.
    
    - Required keys and their values' data types:
        - logical_operator (str): "and" or "or"
        - logical_expressions list([bool | dict]): The logical expressions to evaluate.
    """
    if not expression["logical_operator"] in VALID_LOGICAL_OPERATORS:   # must be "and" or "or"
        raise FilterError("expression logical_operator is not a valid logical operator.")
    return all([is_logical_expression_valid(exp, obj) for exp in expression["logical_expressions"]])

def is_filter_valid(filter: dict, obj: Any = None) -> bool:
    """Determines whether a filter conforms to the format from the documentation.

    Args:
        filter (dict): The filter to check the validity of.
        obj (Any): The object that will be filtered.
            All criteria in the rules must be present and whitelisted for its type.
            Defaults to None.

    Raises:
        ValueError: If the filter dictionary exceeds 100 kilobytes (102,400 bytes).

    Returns:
        bool: Whether the filter is valid.

    - Keys and their required data types:
        - name (str): A print-friendly name for ordering.
        - description (str): A user-friendly description.
        - priority (int): Order of processing, non-negative.
        - object_types (list[str]): All allowed object types.
        - logical_expression (bool | dict): Any logical expression (except filter).
        - multi_value_behavior (str): A string that determines what happens to values returned by an ObjectWrapper.
    """
    # sanity check on dict size
    if getsizeof(filter) > 102400:
        raise ValueError("Size of filter dictionary must be less than or equal to " + \
                         "100 kilobytes (1024 bytes per kilobyte).")
    # filter must contain all of these keys
    if get_logical_expression_type(filter) != "filter":
        return False
    # validate type of each key's value
    if not isinstance(filter["name"], str):
        raise FilterError("filter name is not a string.")
    if not isinstance(filter["description"], str):
        raise FilterError("filter description is not a string.")
    if not isinstance(filter["priority"], int):
        raise FilterError("filter priority is not an int.")
    if not isinstance(filter["object_types"], list):
        raise FilterError("filter object_types is not a list.")
    if not isinstance(filter["logical_expression"], (bool, dict)):
        raise FilterError("filter logical_expression is not a bool or dict.")
    # validate values of keys
    if filter["priority"] < 0:
        raise FilterError("filter priority is less than 0.")
    
    if not is_logical_expression_valid(filter["logical_expression"], obj):
        return False
    # validate obj type
    if obj is not None and not type_name_matches(obj, filter["object_types"]):
        raise FilterError("obj type name is not in filter object_types.")
    
    return True

def sanitize_string(value: str) -> str:
    """Sanitize a string to contain only ASCII characters 32 to 126."""
    return ''.join(char for char in value if 32 <= ord(char) <= 126)

def sanitize_filter(filter: dict) -> dict:
    """Sanitize a dictionary, including nested dictionaries, to ensure
    all string values contain only ASCII characters 32 to 126.

    Args:
        filter (dict): The filter to sanitize.

    Raises:
        TypeError: If the filter is not a dict.

    Returns:
        dict: The new filter, with all characters outside of the ASCII range 32 to 126 removed.
    """
    if not isinstance(filter, dict):
        raise TypeError("filter must be a dictionary.")
    
    sanitized = {}
    for key, value in filter.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_filter(value)  # Recursively sanitize nested dictionaries
        elif isinstance(value, str):
            sanitized[key] = sanitize_string(value)  # Sanitize string values
        else:
            sanitized[key] = value  # Keep other data types unchanged
    return sanitized

def get_value(obj: Any, rule: dict) -> Any:
    """Returns the value of an attribute of `obj`, based on `rule["criterion"]`.

    If the attribute is a method, it must be decorated with `@filter_criterion`
    (unless `obj` is a `ObjectWrapper`). If `rule["parameters"]` is not empty,
    each element of `rule["parameters"]` is passed into the method.

    Args:
        obj (Any): The object that the rule will be executed with.
            All criteria in the rules must be present and whitelisted for its type.
        rule (dict): The rule to execute.

    Raises:
        ValueError: If the criterion is a method without `@filter_criterion`.
        ValueError: If the criterion is a method with `@filter_criterion` but `_is_whitelisted` is False.

    Returns:
        Any: The value of the attribute of `obj`.
    """
    method = getattr(obj, rule["criterion"])
    
    parameters = rule["parameters"]
    if callable(method):
        if not isinstance(obj, ObjectWrapper) and not hasattr(method, "_is_whitelisted"):
            raise AttributeError(f"{method}, a criterion in the filter, does not have the " + \
                                 "@filter_criterion decoractor.")
        elif not isinstance(obj, ObjectWrapper) and not method._is_whitelisted:
            raise ValueError(f"{method}, a criterion in the filter, has the " + \
                             "@filter_criterion decoractor, but _is_whitelisted is set to False.")
        else:
            return method(*parameters)
    else:
        return method

"""
Execution Functions
"""

def execute_logical_expression_on_object(obj: Any, expression: bool | dict) -> bool:
    """Executes a logical expression on an object.

    Args:
        obj (Any): The object that the logical expression will be executed with.
            All criteria in the rules must be present and whitelisted for its type.
        expression (bool | dict): The logical expression (boolean, rule, conditional
            expression, or group expression) to execute.

    Raises:
        ValueError: If expression is not a logical expression of any kind (boolean,
            rule, group expression, conditional expression, or filter)

    Returns:
        bool: The evaluation of the logical expression.
    """
    expression_type = get_logical_expression_type(expression)
    if expression_type == "boolean":
        return expression
    if expression_type == "rule":
        return execute_rule_on_object(obj, expression)
    elif expression_type == "conditional_expression":
        return execute_conditional_expression_on_object(obj, expression)
    elif expression_type == "group_expression":
        return execute_group_expression_on_object(obj, expression)
    elif expression_type == "filter":
        return execute_filter_on_object(obj, expression)
    else:
        raise ValueError("expression is not a logical expression of any kind " + \
                         "(boolean, rule, group expression, conditional expression, or filter)")

def criterion_comparison(
        obj_value: int | float | str | bool, operator: str, comparison_value: int | float | str | bool
    ) -> bool:
    if operator == "<":
        return obj_value < comparison_value
    elif operator == "<=":
        if isinstance(obj_value, (float, Decimal)) or isinstance(comparison_value, (float, Decimal)):
            return obj_value < comparison_value or isclose(obj_value, comparison_value, abs_tol=ABS_TOL)
        return obj_value <= comparison_value
    elif operator == "==":
        if isinstance(obj_value, (float, Decimal)) or isinstance(comparison_value, (float, Decimal)):
            return isclose(obj_value, comparison_value, abs_tol=ABS_TOL)
        return obj_value == comparison_value
    elif operator == "!=":
        if isinstance(obj_value, (float, Decimal)) or isinstance(comparison_value, (float, Decimal)):
            return not isclose(obj_value, comparison_value, abs_tol=ABS_TOL)
        return obj_value != comparison_value
    elif operator == ">=":
        if isinstance(obj_value, (float, Decimal)) or isinstance(comparison_value, (float, Decimal)):
            return obj_value > comparison_value or isclose(obj_value, comparison_value, abs_tol=ABS_TOL)
        return obj_value >= comparison_value
    elif operator == ">":
        return obj_value > comparison_value
    else:
        raise ValueError("operator is invalid.")

def execute_rule_on_object(obj: Any, rule: dict) -> bool:
    """Returns the result of the comparison operation defined by the rule.
    
    Args:
        obj (Any): The object that the rule will be executed with.
            All criteria in the rules must be present and whitelisted for its type.
        rule (dict): The rule to execute.

    Raises:
        ValueError: If rule["comparison_value"] is not valid.

    Returns:
        bool: The result of the comparison.
    """
    if get_logical_expression_type(rule) != "rule":
        raise ValueError("rule does not match the format of a rule.")
    
    obj_value = get_value(obj, rule)
    operator = rule["operator"]
    comparison_value = rule["comparison_value"]

    if isinstance(obj, ObjectWrapper) and isinstance(obj._obj, Iterable):
        multi_value_behavior = rule["multi_value_behavior"]
        if multi_value_behavior == "none":
            raise ValueError("obj is an ObjectWrapper, but multi_value_behavior is set to \"none\".")
        elif multi_value_behavior == "add":
            if isinstance(obj_value[0], str):
                obj_value = ''.join(obj_value)
            elif isinstance(obj_value[0], (int, float, Decimal)):
                obj_value = sum(obj_value)
            else:
                raise TypeError(f"obj.{rule['criterion']} on ObjectWrapper with multi_value_behavior " + \
                                "\"add\" did not return a list of numbers or strings.")
        elif multi_value_behavior == "each_meets_criterion":
            return all([criterion_comparison(get_value(x, rule), operator, comparison_value) for x in obj._obj])
        # ignores comparison_value in favor of checking internal equality of elements
        elif multi_value_behavior == "each_equal_in_object":
            # avoids float comparison imprecision
            return all([criterion_comparison(obj_value[0], "==", val) for val in obj_value[1:]])
        else:
            raise ValueError("multi_value_behavior has an invalid value.")

    return criterion_comparison(obj_value, operator, comparison_value)
    
def execute_conditional_expression_on_object(obj: Any, expression: dict) -> bool:
    """Executes a conditional expression on an object.

    Args:
        obj (Any): The object that the conditional expression will be executed with.
            All criteria in the rules must be present and whitelisted for its type.
        expression (dict): The conditional expression to execute.

    Raises:
        ValueError: If expression does not match the format of a conditional expression.

    Returns:
        bool: The evaluation of the conditional expression.
    """
    if get_logical_expression_type(expression) != "conditional_expression":
        raise ValueError("expression does not match the format of a conditional expression.")
    if execute_logical_expression_on_object(obj, expression["if"]):
        return execute_logical_expression_on_object(obj, expression["then"])
    else:
        return execute_logical_expression_on_object(obj, expression["else"])
    
def execute_group_expression_on_object(obj: Any, expression: dict) -> bool:
    """Executes a group expression on an object.

    Args:
        obj (Any): The object that the group expression will be executed with.
            All criteria in the rules must be present and whitelisted for its type.
        expression (dict): The group expression to execute.

    Raises:
        ValueError: If expression does not match the format of a group expression.
        ValueError: If expression["logical_operator"] != "and" and expression["logical_operator"] != "or"

    Returns:
        bool: The evaluation of the group expression.
    """
    if get_logical_expression_type(expression) != "group_expression":
        raise ValueError("expression does not match the format of a group expression.")
    if expression["logical_operator"] == "and":
        return all([execute_logical_expression_on_object(obj, exp) for exp in expression["logical_expressions"]])
    elif expression["logical_operator"] == "or":
        return any([execute_logical_expression_on_object(obj, exp) for exp in expression["logical_expressions"]])
    else:
        raise ValueError("Group expression's logical operator must be \"and\" or \"or\".")

def execute_filter_on_object(obj, filter: dict, sanitize: bool = True) -> bool:
    """Evaluates a filter on an object.
    Returns True if all logical expressions succeed or False if any of them fail.

    Args:
        obj: Any object.
        filter (dict): A filter to execute.
        sanitize (bool, optional): Whether or not to remove character from the filter outside
            the ASCII range 32 to 126. Defaults to True.

    Raises:
        ValueError: If the filter is not valid, according to the documentation.

    Returns:
        bool: Whether all the logical expressions in the filter evaluated to True.
    """
    if sanitize:
        filter = sanitize_filter(filter)
    if not is_filter_valid(filter, obj):
        raise ValueError("Filter is not valid.")
    
    return execute_logical_expression_on_object(obj, filter["logical_expression"])

def execute_filter_on_array(obj_array: np.ndarray[Any], filter: dict, sanitize: bool = True) -> np.ndarray[bool]:
    """Evaluates a filter on each element in an array.
    Returns an array with the result of evaluating the filter on each element.

    Args:
        obj_array (np.ndarray[Any]): Array of any type of object.
        filter (dict): A filter to execute.
        sanitize (bool, optional): Whether or not to remove character from the filter outside
            the ASCII range 32 to 126. Defaults to True.

    Raises:
        ValueError: If the filter is not valid, according to the documentation.

    Returns:
        np.ndarray[bool]: For each element of obj_array, whether the filter evaluated to True.
    """
    if sanitize:
        filter = sanitize_filter(filter)
    # use first element because np.ndarray element types are homogeneous
    if not is_filter_valid(filter, obj_array[0]):
        raise ValueError("Filter is not valid.")
    
    return np.array([execute_filter_on_object(obj, filter, sanitize=False) for obj in obj_array], dtype=bool)

def sort_filter_list(filter_list: list[dict]) -> list[dict]:
    return sorted(filter_list, key=lambda x: (x["priority"], x["name"]))

def execute_filter_list_on_object(obj: Any, filter_list: list[dict], sanitize: bool = True) -> np.ndarray[bool]:
    """Evaluates a list of filters on an object.
    Returns an array with the evaluation result of each filter.

    This function sorts `filter_list` before executing its elements.
    Filters are primarily ordered by `filter["priority"]` and secondarily ordered by `filter["name"]`.

    Args:
        obj (Any): Any object.
        filter_list (list[dict]): A list of filters to execute on `obj`.
        sanitize (bool, optional): Whether or not to remove character from the filter outside
            the ASCII range 32 to 126. Defaults to True.

    Returns:
        np.ndarray[bool]: For each filter, whether it evaluated to True on `obj`.
    """
    filter_list = sort_filter_list(filter_list)
    if sanitize:
        filter_list = [sanitize_filter(f) for f in filter_list]
    return np.array([execute_filter_on_object(obj, f, sanitize=False) for f in filter_list], dtype=bool)

def execute_filter_list_on_array(
        obj_array: np.ndarray[Any], filter_list: list[dict], sanitize: bool = True
    ) -> np.ndarray[bool]:
    """Evaluates a list of filters on every object in an array.
    Returns an array with the evaluation result of the filter list on each element.

    Args:
        obj_array (np.ndarray[Any]): Array of any type of object.
        filter_list (list[dict]): A list of filters to execute on the elements of `obj_array`.
        sanitize (bool, optional): Whether or not to remove character from the filter outside
            the ASCII range 32 to 126. Defaults to True.

    Returns:
        np.ndarray[bool]: For each element of `obj_array`, whether the filter list evaluated to True.
    """
    filter_list = sort_filter_list(filter_list)
    if sanitize:
        filter_list = [sanitize_filter(f) for f in filter_list]
    return np.array([
        all(execute_filter_list_on_object(obj, filter_list, sanitize=False)) for obj in obj_array
    ], dtype=bool)

def execute_filter_list_on_object_get_first_success(obj: Any, filter_list: list[dict], sanitize: bool = True) -> str:
    """Evaluates a list of filters on an object.
    Returns the name of the first successful filter, if any exists.

    This function sorts `filter_list` before executing its elements.
    Filters are primarily ordered by `filter["priority"]` and secondarily ordered by `filter["name"]`.

    Args:
        obj (Any): Any object.
        filter_list (list[dict]): A list of filters to execute on `obj`.
        sanitize (bool, optional): Whether or not to remove character from
            the filter outside the ASCII range 32 to 126. Defaults to True.

    Raises:
        ValueError: If `obj` did not pass any filter in `filter_list`

    Returns:
        str: The name of the first successful filter in `filter_list`
    """
    filter_list = sort_filter_list(filter_list)
    results = execute_filter_list_on_object(obj, filter_list, sanitize=sanitize)
    for index, passed in enumerate(results):
        if passed:
            return filter_list[index]["name"]
    raise ValueError("obj did not pass any filters in filter_list")

class ObjectWrapper:
    """A class that accepts objects of mixed types.
    Evaluates methods and accesses instance variables and properties for each.
    Ignores presence or lack of @filter_criterion.
    """

    def __init__(self, obj: Any | Iterable[Any]):
        self._obj = obj

    @filter_criterion
    def __getattr__(self, name) -> Any | Callable:
        # Check if all objects in the iterable (or the single object) have the attribute
        if isinstance(self._obj, Iterable):
            if all(hasattr(item, name) for item in self._obj):
                # Return a callable function if the attribute is a method
                if callable(getattr(self._obj[0], name)):
                    def method(*args, **kwargs):
                        return [getattr(item, name)(*args, **kwargs) for item in self._obj]
                    return method
                # Otherwise, return a list of the attribute values
                else:
                    return [getattr(item, name) for item in self._obj]
            else:
                raise AttributeError(f"Not all objects have the attribute '{name}'")
        else:
            if hasattr(self._obj, name):
                attr = getattr(self._obj, name)
                # If the attribute is a method, return it directly
                if callable(attr):
                    return attr
                else:
                    return attr
            else:
                raise AttributeError(f"'{type(self._obj).__name__}' object has no attribute '{name}'")
