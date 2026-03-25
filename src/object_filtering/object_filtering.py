# (c) 2026 Scott Ratchford
# This file is licensed under the MIT License. See LICENSE.txt for details.

import functools
from decimal import Decimal
from inspect import getmro
from sys import getsizeof
from typing import Any, Callable, Iterable, Literal, get_args
from math import isclose

import numpy as np


ABS_TOL = Decimal(0.0001)

Operator = Literal["<", "<=", "==", "!=", ">=", ">"]
VALID_OPERATORS = frozenset(get_args(Operator))

LogicalOperator = Literal["and", "or"]
VALID_LOGICAL_OPERATORS = frozenset(get_args(LogicalOperator))

MultiValueBehavior = Literal["none", "add", "each_meets_criterion", "each_equal_in_object"]
VALID_MULTI_VALUE_BEHAVIORS = frozenset(get_args(MultiValueBehavior))

ClassVariableOperator = Literal["==", "!="]
CLASS_VARIABLE_OPERATORS = frozenset(get_args(ClassVariableOperator))

SPECIAL_VARIABLES = frozenset({"$CLASS$"})

class _LogicalExpressionBase(dict):
    """Base class for all LogicalExpression dict subclasses. Provides dot
    notation access and restricts keys to the set defined by each subclass.
    """
    _valid_keys: frozenset[str] = frozenset()
    _key_aliases: dict[str, str] = {}

    def _resolve_key(self, key: str) -> str:
        return self._key_aliases.get(key, key)

    def __setitem__(self, key, value):
        if key not in self._valid_keys:
            raise KeyError(
                f"'{key}' is not a valid key for {type(self).__name__}. "
                f"Valid keys: {sorted(self._valid_keys)}"
            )
        super().__setitem__(key, value)

    def __delitem__(self, key):
        raise TypeError(f"Cannot delete keys from {type(self).__name__}.")

    def __getattr__(self, name):
        resolved = self._resolve_key(name)
        if resolved in self._valid_keys:
            try:
                return self[resolved]
            except KeyError:
                raise AttributeError(
                    f"'{type(self).__name__}' has no key '{resolved}'"
                )
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        resolved = self._resolve_key(name)
        if resolved in self._valid_keys:
            self[resolved] = value
        else:
            raise AttributeError(
                f"'{name}' is not a valid attribute for {type(self).__name__}."
            )

class ObjectFilter(_LogicalExpressionBase):
    _valid_keys = frozenset({"name", "description", "priority", "object_types", "logical_expression"})

    name: str
    description: str
    priority: int
    object_types: list
    logical_expression: bool | dict

    def __init__(
            self,
            name: str = "",
            description: str = "",
            priority: int = 0,
            object_types: list = ["object"],
            logical_expression: bool | dict = True
        ) -> None:
        super().__init__()
        self["name"] = name
        self["description"] = description
        self["priority"] = priority
        self["object_types"] = object_types
        self["logical_expression"] = logical_expression

    @classmethod
    def from_dict(cls, d: dict) -> "ObjectFilter":
        """Creates an ObjectFilter from a plain dict, recursively converting
        nested LogicalExpressions.

        Args:
            d (dict): A dictionary with ObjectFilter keys.

        Raises:
            KeyError: If d contains unrecognized keys or is missing required
                keys.
            TypeError: If value types do not match expectations.

        Returns:
            ObjectFilter: The constructed ObjectFilter.
        """
        _check_keys(d, cls._valid_keys, cls.__name__)
        if not isinstance(d["name"], str):
            raise TypeError("name must be a str.")
        if not isinstance(d["description"], str):
            raise TypeError("description must be a str.")
        if not isinstance(d["priority"], int):
            raise TypeError("priority must be an int.")
        if not isinstance(d["object_types"], list):
            raise TypeError("object_types must be a list.")
        return cls(
            name=d["name"],
            description=d["description"],
            priority=d["priority"],
            object_types=d["object_types"],
            logical_expression=logical_expression_from_dict(d["logical_expression"])
        )

class Rule(_LogicalExpressionBase):
    _valid_keys = frozenset({"criterion", "operator", "comparison_value", "parameters", "multi_value_behavior"})

    criterion: str
    operator: Operator
    comparison_value: int | float | str | bool
    parameters: list
    multi_value_behavior: MultiValueBehavior

    def __init__(
            self,
            criterion: str = "__class__",
            operator: Operator = "==",
            comparison_value: int | float | str | bool = "",
            parameters: list = [],
            multi_value_behavior: MultiValueBehavior = "none"
        ) -> None:
        super().__init__()
        self["criterion"] = criterion
        self["operator"] = operator
        self["comparison_value"] = comparison_value
        self["parameters"] = parameters
        self["multi_value_behavior"] = multi_value_behavior

    @classmethod
    def from_dict(cls, d: dict) -> "Rule":
        """Creates a Rule from a plain dict.

        Args:
            d (dict): A dictionary with Rule keys.

        Raises:
            KeyError: If d contains unrecognized keys or is missing required
                keys.
            ValueError: If operator or multi_value_behavior values are not
                valid.

        Returns:
            Rule: The constructed Rule.
        """
        _check_keys(d, cls._valid_keys, cls.__name__)
        if not isinstance(d["criterion"], str):
            raise TypeError("criterion must be a str.")
        if d["operator"] not in VALID_OPERATORS:
            raise ValueError(
                f"operator must be one of {sorted(VALID_OPERATORS)}, "
                f"got '{d['operator']}'."
            )
        if not isinstance(d["parameters"], list):
            raise TypeError("parameters must be a list.")
        if d["multi_value_behavior"] not in VALID_MULTI_VALUE_BEHAVIORS:
            raise ValueError(
                f"multi_value_behavior must be one of "
                f"{sorted(VALID_MULTI_VALUE_BEHAVIORS)}, "
                f"got '{d['multi_value_behavior']}'."
            )
        return cls(
            criterion=d["criterion"],
            operator=d["operator"],
            comparison_value=d["comparison_value"],
            parameters=d["parameters"],
            multi_value_behavior=d["multi_value_behavior"]
        )

class GroupExpression(_LogicalExpressionBase):
    _valid_keys = frozenset({"logical_operator", "logical_expressions"})

    logical_operator: LogicalOperator
    logical_expressions: 'list[LogicalExpression]'

    def __init__(
            self,
            logical_operator: LogicalOperator = "and",
            logical_expressions: 'list[LogicalExpression]' = []
        ) -> None:
        super().__init__()
        self["logical_operator"] = logical_operator
        self["logical_expressions"] = logical_expressions

    @classmethod
    def from_dict(cls, d: dict) -> "GroupExpression":
        """Creates a GroupExpression from a plain dict, recursively converting
        nested LogicalExpressions.

        Args:
            d (dict): A dictionary with GroupExpression keys.

        Raises:
            KeyError: If d contains unrecognized keys or is missing required
                keys.
            ValueError: If logical_operator is not valid.

        Returns:
            GroupExpression: The constructed GroupExpression.
        """
        _check_keys(d, cls._valid_keys, cls.__name__)
        if d["logical_operator"] not in VALID_LOGICAL_OPERATORS:
            raise ValueError(
                f"logical_operator must be one of "
                f"{sorted(VALID_LOGICAL_OPERATORS)}, "
                f"got '{d['logical_operator']}'."
            )
        if not isinstance(d["logical_expressions"], list):
            raise TypeError("logical_expressions must be a list.")
        return cls(
            logical_operator=d["logical_operator"],
            logical_expressions=[
                logical_expression_from_dict(exp)
                for exp in d["logical_expressions"]
            ]
        )

class ConditionalExpression(_LogicalExpressionBase):
    _valid_keys = frozenset({"if", "then", "else"})
    _key_aliases = {"_if": "if", "_then": "then", "_else": "else"}

    _if: bool | dict
    _then: bool | dict
    _else: bool | dict

    def __init__(
            self,
            _if: bool | dict = True,
            _then: bool | dict = True,
            _else: bool | dict = True
        ) -> None:
        super().__init__()
        self["if"] = _if
        self["then"] = _then
        self["else"] = _else

    @classmethod
    def from_dict(cls, d: dict) -> "ConditionalExpression":
        """Creates a ConditionalExpression from a plain dict, recursively
        converting nested LogicalExpressions.

        Args:
            d (dict): A dictionary with ConditionalExpression keys.

        Raises:
            KeyError: If d contains unrecognized keys or is missing required
                keys.

        Returns:
            ConditionalExpression: The constructed ConditionalExpression.
        """
        _check_keys(d, cls._valid_keys, cls.__name__)
        return cls(
            _if=logical_expression_from_dict(d["if"]),
            _then=logical_expression_from_dict(d["then"]),
            _else=logical_expression_from_dict(d["else"])
        )

LogicalExpression = bool | Rule | ConditionalExpression | GroupExpression | ObjectFilter

def _check_keys(d: dict, valid_keys: frozenset[str], class_name: str) -> None:
    """Validates that a dict has exactly the expected keys.

    Args:
        d (dict): The dictionary to check.
        valid_keys (frozenset[str]): The set of required keys.
        class_name (str): The name of the target class, for error messages.

    Raises:
        KeyError: If there are missing or extra keys.
    """
    key_set = set(d.keys())
    missing = valid_keys - key_set
    extra = key_set - valid_keys
    if missing:
        raise KeyError(
            f"Missing keys for {class_name}: {sorted(missing)}"
        )
    if extra:
        raise KeyError(
            f"Unrecognized keys for {class_name}: {sorted(extra)}"
        )

def logical_expression_from_dict(expression: bool | dict) -> LogicalExpression:
    """Converts a plain dict (or bool) into the appropriate LogicalExpression
    subclass, recursively converting any nested expressions.

    Args:
        expression (bool | dict): A bool or dict representing a
            LogicalExpression.

    Raises:
        TypeError: If expression is not a bool or dict.
        ValueError: If the dict's keys do not match any LogicalExpression
            type.

    Returns:
        LogicalExpression: The constructed LogicalExpression.
    """
    if isinstance(expression, bool):
        return expression
    if isinstance(expression, _LogicalExpressionBase):
        return expression
    if not isinstance(expression, dict):
        raise TypeError(
            f"Expected a bool or dict, got {type(expression).__name__}."
        )
    expr_type = get_logical_expression_type(expression)
    if expr_type == Rule:
        return Rule.from_dict(expression)
    elif expr_type == ConditionalExpression:
        return ConditionalExpression.from_dict(expression)
    elif expr_type == GroupExpression:
        return GroupExpression.from_dict(expression)
    elif expr_type == ObjectFilter:
        return ObjectFilter.from_dict(expression)
    else:
        raise ValueError("Dict keys do not match any LogicalExpression type.")

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
    """Evaluates whether obj is an instance of a class with a name matching
    target_type_name. If obj is an ObjectWrapper, the types of the elements of
    obj._obj are checked instead.

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

def dict_to_logical_expression(d: dict) -> LogicalExpression:
    """Converts a plain dict into the appropriate LogicalExpression subclass,
    recursively converting any nested expressions.

    Args:
        d (dict): A dict whose keys match a LogicalExpression type.

    Raises:
        ValueError: If the dict's keys do not match any LogicalExpression type.

    Returns:
        LogicalExpression: The constructed LogicalExpression.
    """
    expr_type = get_logical_expression_type(d)
    if expr_type == Rule:
        return Rule.from_dict(d)
    elif expr_type == ConditionalExpression:
        return ConditionalExpression.from_dict(d)
    elif expr_type == GroupExpression:
        return GroupExpression.from_dict(d)
    elif expr_type == ObjectFilter:
        return ObjectFilter.from_dict(d)

def get_logical_expression_type(
        expression: LogicalExpression
    ) -> type[bool] | type[Rule] | type[ConditionalExpression] | type[GroupExpression] | type[ObjectFilter]:
    """Determines the type of a LogicalExpression based on its contents.

    Args:
        expression (LogicalExpression): A LogicalExpression to evaluate.

    Raises:
        TypeError: If expression is not a LogicalExpression.
        ValueError: If expression is a dict but its keys do not match any
            LogicalExpression.

    Returns:
        type: bool, Rule, ConditionalExpression, GroupExpression, ObjectFilter
    """
    if isinstance(expression, bool):
        return bool
    elif not isinstance(expression, dict):
        raise TypeError("expression is not a bool or dict")
    key_set = set(expression.keys())
    if {"criterion", "operator", "comparison_value", "parameters", "multi_value_behavior"}.issubset(key_set):
        return Rule
    if {"if", "then", "else"}.issubset(key_set):
        return ConditionalExpression
    if {"logical_operator", "logical_expressions"}.issubset(key_set):
        return GroupExpression
    if {"name", "description", "priority", "object_types", "logical_expression"}.issubset(key_set):
        return ObjectFilter

    raise ValueError("expression is not a LogicalExpression.")

def is_logical_expression_valid(expression: LogicalExpression, obj: Any = None) -> bool:
    """Determines whether a LogicalExpression conforms to the format from the
    documentation.

    Args:
        expression (LogicalExpression): The LogicalExpression to check the
            validity of.
        obj (Any): The object that will be filtered. All criteria in the Rules
            must be present and whitelisted for its type. Defaults to None. If
                None, criteria validity checks will be skipped.

    Raises:
        ValueError: If expression is not a LogicalExpression

    Returns:
        bool: Whether the LogicalExpression is valid.
    """
    if isinstance(expression, dict) and not isinstance(expression, _LogicalExpressionBase):
        expression = dict_to_logical_expression(expression)
    expr_type = get_logical_expression_type(expression)
    if expr_type == bool:
        # True and False are both valid
        return True
    elif expr_type == Rule:
        return is_rule_valid(expression, obj)
    elif expr_type == ConditionalExpression:
        return is_conditional_expression_valid(expression, obj)
    elif expr_type == GroupExpression:
        return is_group_expression_valid(expression, obj)
    elif expr_type == ObjectFilter:
        return is_filter_valid(expression, obj)
    else:
        raise ValueError("expression is not a LogicalExpression.")

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
    if isinstance(rule, dict) and not isinstance(rule, _LogicalExpressionBase):
        rule = dict_to_logical_expression(rule)
    if get_logical_expression_type(rule) != Rule:
        raise FilterError("rule is not a Rule.")
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
        # special variable handling
        if rule["criterion"] in SPECIAL_VARIABLES:
            if rule["criterion"] == "$CLASS$" and rule["operator"] not in CLASS_VARIABLE_OPERATORS:
                raise FilterError("$CLASS$ only supports == and != operators.")
            return True
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

def is_conditional_expression_valid(expression: ConditionalExpression, obj: Any = None) -> bool:
    """Determines whether a ConditionalExpression conforms to the format from
    the documentation. Raises an error if the ConditionalExpression is not
    valid.

    Args:
        expression (dict): The ConditionalExpression to check the validity of.
        obj (Any): The object that will be filtered. All criteria in the Rules
            must be present and whitelisted for its type. Defaults to None.

    Returns:
        bool: Whether the conditional expression is valid.
    
    - Required keys and their values' data types:
        - if (LogicalExpression): The first LogicalExpression to evaluate
        - then (LogicalExpression): The LogicalExpression to evaluate if the
            "if" branch evaluates to True.
        - else (LogicalExpression): The LogicalExpression to evaluate if the
            "if" branch evaluates to False.
    """
    if isinstance(expression, dict) and not isinstance(expression, _LogicalExpressionBase):
        expression = dict_to_logical_expression(expression)
    if get_logical_expression_type(expression) != ConditionalExpression:
        raise FilterError("expression is not a ConditionalExpression.")
    return all([is_logical_expression_valid(exp, obj) for exp in expression.values()])

def is_group_expression_valid(expression: GroupExpression, obj: Any = None) -> bool:
    """Determines whether the GroupExpression conforms to the format from the
    documentation.

    Args:
        expression (GroupExpression): The GroupExpression to check the validity
            of.
        obj (Any): The object that will be filtered. All criteria in the Rules
            must be present and whitelisted for its type. Defaults to None.

    Returns:
        bool: Whether the GroupExpression is valid.
    
    - Required keys and their values' data types:
        - logical_operator (str): "and" or "or"
        - logical_expressions (list[LogicalExpression]): The LogicalExpressions
            to evaluate.
    """
    if isinstance(expression, dict) and not isinstance(expression, _LogicalExpressionBase):
        expression = dict_to_logical_expression(expression)
    if not expression["logical_operator"] in VALID_LOGICAL_OPERATORS:   # must be "and" or "or"
        raise FilterError("expression logical_operator is not a valid logical operator.")
    return all([is_logical_expression_valid(exp, obj) for exp in expression["logical_expressions"]])

def is_filter_valid(filter: ObjectFilter, obj: Any = None) -> bool:
    """Determines whether an ObjectFilter conforms to the format from the
    documentation.

    Args:
        filter (ObjectFilter): The ObjectFilter to check the validity of.
        obj (Any): The object that will be filtered. All criteria in the Rules
            must be present and whitelisted for its type. Defaults to None.

    Raises:
        ValueError: If the ObjectFilter exceeds 100 kilobytes (102,400 bytes)

    Returns:
        bool: Whether the ObjectFilter is valid.

    - Keys and their required data types:
        - name (str): A print-friendly name for ordering.
        - description (str): A user-friendly description.
        - priority (int): Order of processing, non-negative.
        - object_types (list[str]): All allowed object types.
        - logical_expression (bool | dict): May be any type of
            LogicalExpression except an ObjectFilter.
        - multi_value_behavior (str): A string that determines what happens to
            values returned by an ObjectWrapper.
    """
    if isinstance(filter, dict) and not isinstance(filter, _LogicalExpressionBase):
        filter = dict_to_logical_expression(filter)
    # sanity check on dict size
    if getsizeof(filter) > 102400:
        raise ValueError("Size of filter dictionary must be less than or equal to " + \
                         "100 kilobytes (1024 bytes per kilobyte).")
    # filter must contain all of these keys
    if get_logical_expression_type(filter) != ObjectFilter:
        return False
    # validate type of each key's value
    if not isinstance(filter["name"], str):
        raise TypeError("filter name is not a string.")
    if not isinstance(filter["description"], str):
        raise TypeError("filter description is not a string.")
    if not isinstance(filter["priority"], int):
        raise TypeError("filter priority is not an int.")
    if not isinstance(filter["object_types"], list):
        raise TypeError("filter object_types is not a list.")
    if not isinstance(filter["logical_expression"], (bool, dict)):
        raise TypeError("filter logical_expression is not a LogicalExpression.")
    # validate values of keys
    if filter["priority"] < 0:
        raise ValueError("filter priority is less than 0.")
    
    if not is_logical_expression_valid(filter["logical_expression"], obj):
        return False
    # validate obj type
    if obj is not None and not type_name_matches(obj, filter["object_types"]):
        raise FilterError("obj type name is not in filter object_types.")
    
    return True

def sanitize_string(value: str) -> str:
    """Sanitize a string to contain only ASCII characters 32 to 126."""
    return ''.join(char for char in value if 32 <= ord(char) <= 126)

def sanitize_filter(filter: ObjectFilter) -> ObjectFilter:
    """Sanitize an ObjectFilter, including nested LogicalExpressions, to ensure
    all string values contain only ASCII characters 32 to 126. Returns an
    altered deep copy while preserving the original.

    Args:
        filter (ObjectFilter): The ObjectFilter to sanitize.

    Raises:
        TypeError: If the ObjectFilter is not a dict.

    Returns:
        ObjectFilter: The new ObjectFilter, with all characters outside of the
            ASCII range 32 to 126 removed.
    """
    if isinstance(filter, dict) and not isinstance(filter, _LogicalExpressionBase):
        filter = dict_to_logical_expression(filter)
    if not isinstance(filter, dict):
        raise TypeError("filter must be an ObjectFilter.")

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
    """Returns the value of an attribute of `obj`, based on
    `rule["criterion"]`.

    If the attribute is a method, it must be decorated with `@filter_criterion`
    (unless `obj` is a `ObjectWrapper`). If `rule["parameters"]` is not empty,
    each element of `rule["parameters"]` is passed into the method.

    Args:
        obj (Any): The object that the rule will be executed with. All criteria
            in the rules must be present and whitelisted for its type.
        rule (dict): The rule to execute.

    Raises:
        ValueError: If the criterion is a method without `@filter_criterion`.
        ValueError: If the criterion is a method with `@filter_criterion` but
            `_is_whitelisted` is False.

    Returns:
        Any: The value of the attribute of `obj`.
    """
    if isinstance(rule, dict) and not isinstance(rule, _LogicalExpressionBase):
        rule = dict_to_logical_expression(rule)
    # special variable handling
    if rule["criterion"] == "$CLASS$":
        if isinstance(obj, ObjectWrapper):
            if isinstance(obj._obj, Iterable):
                return [type(element).__name__ for element in obj._obj]
            return type(obj._obj).__name__
        return type(obj).__name__

    method = getattr(obj, rule["criterion"])

    parameters = rule["parameters"]
    if callable(method):
        if not isinstance(obj, ObjectWrapper) and not hasattr(method, "_is_whitelisted"):
            raise AttributeError(
                f"{method}, a criterion in the ObjectFilter, does not have the @filter_criterion decorator."
            )
        elif not isinstance(obj, ObjectWrapper) and not method._is_whitelisted:
            raise ValueError(
                f"{method}, a criterion in the ObjectFilter, has the @filter_criterion decorator, but _is_whitelisted is set to False."
            )
        else:
            return method(*parameters)
    else:
        return method

"""
Execution Functions
"""

def execute_logical_expression_on_object(obj: Any, expression: LogicalExpression) -> bool:
    """Executes a LogicalExpression on an object.

    Args:
        obj (Any): The object that the LogicalExpression will be executed with.
            All criteria in the Rules must be present and whitelisted for its
            type.
        expression (LogicalExpression): The LogicalExpression to execute.

    Raises:
        ValueError: If expression is not a LogicalExpression

    Returns:
        bool: The evaluation of the LogicalExpression
    """
    if isinstance(expression, dict) and not isinstance(expression, _LogicalExpressionBase):
        expression = dict_to_logical_expression(expression)
    expression_type = get_logical_expression_type(expression)
    if expression_type == bool:
        return expression
    if expression_type == Rule:
        return execute_rule_on_object(obj, expression)
    elif expression_type == ConditionalExpression:
        return execute_conditional_expression_on_object(obj, expression)
    elif expression_type == GroupExpression:
        return execute_group_expression_on_object(obj, expression)
    elif expression_type == ObjectFilter:
        return execute_filter_on_object(obj, expression)
    else:
        raise ValueError("expression is not a LogicalExpression.")

def criterion_comparison(
        obj_value: int | float | str | bool,
        operator: Operator,
        comparison_value: int | float | str | bool
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
        obj (Any): The object that the rule will be executed with. All criteria
            in the rules must be present and whitelisted for its type.
        rule (dict): The rule to execute.

    Raises:
        ValueError: If rule["comparison_value"] is not valid.

    Returns:
        bool: The result of the comparison.
    """
    if isinstance(rule, dict) and not isinstance(rule, _LogicalExpressionBase):
        rule = dict_to_logical_expression(rule)
    if get_logical_expression_type(rule) != Rule:
        raise ValueError("rule is not a Rule.")

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
    if isinstance(expression, dict) and not isinstance(expression, _LogicalExpressionBase):
        expression = dict_to_logical_expression(expression)
    if get_logical_expression_type(expression) != ConditionalExpression:
        raise ValueError("expression is not a ConditionalExpression.")
    if execute_logical_expression_on_object(obj, expression["if"]):
        return execute_logical_expression_on_object(obj, expression["then"])
    else:
        return execute_logical_expression_on_object(obj, expression["else"])
    
def execute_group_expression_on_object(obj: Any, expression: GroupExpression) -> bool:
    """Executes a GroupExpression on an object.

    Args:
        obj (Any): The object that the GroupExpression will be executed with.
            All criteria in the rules must be present and whitelisted for its type.
        expression (GroupExpression): The GroupExpression to execute.

    Raises:
        ValueError: If expression does not match the format of a GroupExpression.
        ValueError: If expression["logical_operator"] is not "and" or "or"

    Returns:
        bool: The evaluation of the GroupExpression.
    """
    if isinstance(expression, dict) and not isinstance(expression, _LogicalExpressionBase):
        expression = dict_to_logical_expression(expression)
    if get_logical_expression_type(expression) != GroupExpression:
        raise ValueError("expression is not a GroupExpression.")
    if expression["logical_operator"] == "and":
        return all([execute_logical_expression_on_object(obj, exp) for exp in expression["logical_expressions"]])
    elif expression["logical_operator"] == "or":
        return any([execute_logical_expression_on_object(obj, exp) for exp in expression["logical_expressions"]])
    else:
        raise ValueError("GroupExpression's logical operator must be \"and\" or \"or\".")

def execute_filter_on_object(obj, filter: ObjectFilter, sanitize: bool = True) -> bool:
    """Evaluates a ObjectFilter on an object. Returns True if all
    LogicalExpressions succeed or False if any fail.

    Args:
        obj: Any object.
        filter (ObjectFilter): An ObjectFilter to execute.
        sanitize (bool, optional): Whether or not to santize the ObjectFilters
            before execution. Defaults to True.

    Raises:
        ValueError: If the ObjectFilter is not valid, according to the
            documentation.

    Returns:
        bool: Whether all the LogicalExpressions in the ObjectFilter evaluated
            to True.
    """
    if isinstance(filter, dict) and not isinstance(filter, _LogicalExpressionBase):
        filter = dict_to_logical_expression(filter)
    if sanitize:
        filter = sanitize_filter(filter)
    if not is_filter_valid(filter, obj):
        raise ValueError("ObjectFilter is not valid.")

    return execute_logical_expression_on_object(obj, filter["logical_expression"])

def execute_filter_on_array(obj_array: np.ndarray[Any], filter: dict, sanitize: bool = True) -> np.ndarray[bool]:
    """Evaluates an ObjectFilter on each element in an array. Returns an array
    with the result of evaluating the ObjectFilter on each element.

    Args:
        obj_array (np.ndarray[Any]): Array of any type of object.
        filter (ObjectFilter): An ObjectFilter to execute.
        sanitize (bool, optional): Whether or not to santize the ObjectFilters
            before execution. Defaults to True.

    Raises:
        ValueError: If the ObjectFilter is not valid, according to the
            documentation.

    Returns:
        np.ndarray[bool]: For each element of obj_array, whether the
            ObjectFilter evaluated to True.
    """
    if isinstance(filter, dict) and not isinstance(filter, _LogicalExpressionBase):
        filter = dict_to_logical_expression(filter)
    if sanitize:
        filter = sanitize_filter(filter)
    # use first element because np.ndarray element types are homogeneous
    if not is_filter_valid(filter, obj_array[0]):
        raise ValueError("ObjectFilter is not valid.")
    
    return np.array([execute_filter_on_object(obj, filter, sanitize=False) for obj in obj_array], dtype=bool)

def sort_filter_list(filter_list: list[dict]) -> list[dict]:
    filter_list = [dict_to_logical_expression(f) if isinstance(f, dict) and not isinstance(f, _LogicalExpressionBase) else f for f in filter_list]
    return sorted(filter_list, key=lambda x: (x["priority"], x["name"]))

def execute_filter_list_on_object(
        obj: Any,
        filter_list: list[ObjectFilter],
        sanitize: bool = True
    ) -> np.ndarray[bool]:
    """Evaluates a list of filters on an object. Returns an array with the
    evaluation result of each ObjectFilter.

    This function sorts `filter_list` before executing its elements.
    ObjectFilters are primarily ordered by priority (ascending) and secondarily
    ordered by name (ascending).

    Args:
        obj (Any): Any object.
        filter_list (list[ObjectFilter]): A list of ObjectFilter to execute on
            `obj`.
        sanitize (bool, optional): Whether or not to santize the ObjectFilters
            before execution. Defaults to True.

    Returns:
        np.ndarray[bool]: For each ObjectFilter, whether it evaluated to True
            on `obj`.
    """
    filter_list = [dict_to_logical_expression(f) if isinstance(f, dict) and not isinstance(f, _LogicalExpressionBase) else f for f in filter_list]
    filter_list = sort_filter_list(filter_list)
    if sanitize:
        filter_list = [sanitize_filter(f) for f in filter_list]
    return np.array([execute_filter_on_object(obj, f, sanitize=False) for f in filter_list], dtype=bool)

def execute_filter_list_on_array(
        obj_array: np.ndarray[Any],
        filter_list: list[dict],
        sanitize: bool = True
    ) -> np.ndarray[bool]:
    """Evaluates a list of filters on every object in an array. Returns an
    array with the evaluation result of the ObjectFilter list on each element.

    Args:
        obj_array (np.ndarray[Any]): Array of any type of object.
        filter_list (list[dict]): A list of ObjectFilters to execute on the
            elements of `obj_array`.
        sanitize (bool, optional): Whether or not to santize the ObjectFilters
            before execution. Defaults to True.

    Returns:
        np.ndarray[bool]: For each element of `obj_array`, whether the
            ObjectFilter list evaluated to True.
    """
    filter_list = [dict_to_logical_expression(f) if isinstance(f, dict) and not isinstance(f, _LogicalExpressionBase) else f for f in filter_list]
    filter_list = sort_filter_list(filter_list)
    if sanitize:
        filter_list = [sanitize_filter(f) for f in filter_list]
    return np.array([
        all(execute_filter_list_on_object(obj, filter_list, sanitize=False)) for obj in obj_array
    ], dtype=bool)

def execute_filter_list_on_object_get_first_success(
        obj: Any,
        filter_list: list[ObjectFilter],
        sanitize: bool = True
    ) -> str:
    """Evaluates a list of ObjectFilters on an object. Returns the name of the
    first successful filter, if any exists.

    This function sorts `filter_list` before executing its elements.
    ObjectFilters are primarily ordered by `filter["priority"]` and secondarily
    ordered by `filter["name"]`.

    Args:
        obj (Any): Any object.
        filter_list (list[ObjectFilter]): A list of ObjectFilters to execute
            on `obj`.
        sanitize (bool, optional): Whether or not to santize the ObjectFilters
            before execution. Defaults to True.

    Raises:
        ValueError: If `obj` did not pass any ObjectFilter in `filter_list`

    Returns:
        str: The name of the first successful ObjectFilter in `filter_list`
    """
    filter_list = [dict_to_logical_expression(f) if isinstance(f, dict) and not isinstance(f, _LogicalExpressionBase) else f for f in filter_list]
    filter_list = sort_filter_list(filter_list)
    results = execute_filter_list_on_object(obj, filter_list, sanitize=sanitize)
    for index, passed in enumerate(results):
        if passed:
            return filter_list[index]["name"]
    raise ValueError("obj did not pass any ObjectFilters in filter_list")

class ObjectWrapper:
    """A class that accepts objects of mixed types. Evaluates methods and
    accesses instance variables and properties for each. Ignores presence or
    lack of @filter_criterion.
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
