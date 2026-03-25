# (c) 2026 Scott Ratchford
# This file is licensed under the MIT License. See LICENSE.txt for details.

import unittest

from src import object_filtering

import pytest


class Shape:
    def __init__(self, x: int | float, y: int | float):
        self.x: int | float = x
        self.y: int | float = y

    @object_filtering.filter_criterion
    def area(self) -> int | float:
        return self.x * self.y
    
    @object_filtering.filter_criterion
    def volume(self, z: int | float) -> int | float:
        return self.area() * z
    
    def secret_method(self) -> None:
        return
    
class Point:
    def __init__(self, x: int | float, y: int | float) -> None:
        self.x: int | float = x
        self.y: int | float = y

    @object_filtering.filter_criterion
    def area(self) -> int:
        return 0
    
    @object_filtering.filter_criterion
    def volume(self, z: int | float = 0) -> int:
        return 0
    
    def secret_method(self) -> None:
        return

SHAPE_1 = Shape(1, 2)
SHAPE_2 = Shape(2, 4)
SHAPE_3 = Shape(3, 6)

SHAPE_BIG = Shape(3, 4)
SHAPE_MEDIUM = Shape(2, 2)
SHAPE_SMALL = Shape(1, 1)

RULE_X = {
    "criterion": "x",
    "operator": ">=",
    "comparison_value": 2,
    "parameters": [],
    "multi_value_behavior": "add"
}

RULE_Y = {
    "criterion": "y",
    "operator": ">=",
    "comparison_value": 2,
    "parameters": [],
    "multi_value_behavior": "add"
}

RULE_AREA = {
    "criterion": "area",
    "operator": ">=",
    "comparison_value": 4,
    "parameters": [],
    "multi_value_behavior": "add"
}

RULE_VOLUME = {
    "criterion": "volume",
    "operator": ">=",
    "comparison_value": 8,
    "parameters": [2],
    "multi_value_behavior": "add"
}

RULE_SECRET = {
    "criterion": "secret_method",
    "operator": "!=",
    "comparison_value": True,
    "parameters": [],
    "multi_value_behavior": "none"
}

RULE_MULTI_NONE = {
    "criterion": "area",
    "operator": ">=",
    "comparison_value": 0,
    "parameters": [],
    "multi_value_behavior": "none"
}

RULE_MULTI_ADD = {
    "criterion": "area",
    "operator": "==",
    "comparison_value": 16,
    "parameters": [],
    "multi_value_behavior": "add"
}

RULE_MULTI_MEET = {
    "criterion": "area",
    "operator": ">=",
    "comparison_value": 8,
    "parameters": [],
    "multi_value_behavior": "each_meets_criterion"
}

RULE_MULTI_EQUAL = {
    "criterion": "area",
    "operator": "==",
    "comparison_value": True,
    "parameters": [],
    "multi_value_behavior": "each_equal_in_object"
}

CONDITIONAL_1 = { 
    "if": {
        "criterion": "x",
        "operator": ">=",
        "comparison_value": 2,
        "parameters": [],
        "multi_value_behavior": "add"
    },
    "then": {
        "criterion": "y",
        "operator": ">=",
        "comparison_value": 1,
        "parameters": [],
        "multi_value_behavior": "add"
    },
    "else": False
}

CONDITIONAL_2 = { 
    "if": {
        "criterion": "y",
        "operator": ">=",
        "comparison_value": 2,
        "parameters": [],
        "multi_value_behavior": "add"
    },
    "then": {
        "criterion": "x",
        "operator": ">=",
        "comparison_value": 1,
        "parameters": [],
        "multi_value_behavior": "add"
    },
    "else": False
}

GROUP_1 = {
    "logical_operator": "and",
    "logical_expressions": [
        RULE_X,
        RULE_Y,
        RULE_VOLUME
    ]
}

GROUP_2 = {
    "logical_operator": "or",
    "logical_expressions": [
        RULE_X,
        RULE_Y,
        RULE_VOLUME
    ]
}

SHAPE_FILTER_1 = {
    "name": "Shape Size: Logical Block",
    "description": "Used to determine whether Shapes are larger than 2x2.",
    "priority": 1,
    "object_types": ["Shape"],
    "logical_expression": {
        "logical_operator": "and",
        "logical_expressions": [
            {
                "criterion": "x",
                "operator": ">=",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "add"
            },
            {
                "criterion": "y",
                "operator": ">=",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "add"
            },
            {
                "criterion": "area",
                "operator": ">=",
                "comparison_value": 4,
                "parameters": [],
                "multi_value_behavior": "add"
            }
        ]
    }
}

SHAPE_FILTER_2 = {
    "name": "Shape Size: Nested Logical Blocks",
    "description": "Used to determine whether Shapes are larger than 1x2.",
    "priority": 1,
    "object_types": ["Shape"],
    "logical_expression": {
        "logical_operator": "and",
        "logical_expressions": [
            {
                "criterion": "x",
                "operator": ">=",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "add"
            },
            {
                "criterion": "y",
                "operator": ">=",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "add"
            },
            {
                "logical_operator": "and",
                "logical_expressions": [
                    {
                        "criterion": "area",
                        "operator": ">=",
                        "comparison_value": 2,
                        "parameters": [],
                        "multi_value_behavior": "add"
                    },
                    True
                ]
            }
        ]
    }
}

SHAPE_FILTER_3 = {
    "name": "Shape Size: Branch",
    "description": "Used to determine whether Shapes are larger than 1x2.",
    "priority": 1,
    "object_types": ["Shape"],
    "logical_expression": {
        "if": {
            "criterion": "x",
            "operator": ">=",
            "comparison_value": 1,
            "parameters": [],
            "multi_value_behavior": "add"
        },
        "then": {
            "criterion": "y",
            "operator": ">=",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "add"
        },
        "else": {
            "criterion": "area",
            "operator": ">=",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "add"
        }
    }
}

SHAPE_FILTER_4 = {
    "name": "Shape Size: Branch Alt",
    "description": "Used to determine whether Shapes are larger than 1x2.",
    "priority": 1,
    "object_types": ["Shape"],
    "logical_expression": {
        "if": {
            "criterion": "x",
            "operator": ">=",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "add"
        },
        "then": {
            "criterion": "y",
            "operator": ">=",
            "comparison_value": 1,
            "parameters": [],
            "multi_value_behavior": "add"
        },
        "else": {
            "criterion": "area",
            "operator": ">=",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "add"
        }
    }
}

SHAPE_FILTER_5 = {
    "name": "Shape Size: Simple",
    "description": "Used to determine whether Shapes are larger than 1x2.",
    "priority": 1,
    "object_types": ["Shape"],
    "logical_expression": {
        "criterion": "area",
        "operator": ">=",
        "comparison_value": 2,
        "parameters": [],
        "multi_value_behavior": "add"
    }
}

SHAPE_FILTER_6 = {
    "name": "Shape Size: Simple",
    "description": "Used to determine whether Shapes are larger than 1x2.",
    "priority": 1,
    "object_types": ["Shape"],
    "logical_expression": {
        "name": "Shape Size: Simple",
        "description": "Used to determine whether Shapes are larger than 1x2.",
        "priority": 1,
        "object_types": ["Shape"],
        "logical_expression": {
            "criterion": "area",
            "operator": ">=",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "add"
        }
    }
}

SHAPE_FILTER_FLOAT = {
    "name": "Float Filter",
    "description": "Used to test float comparisons in filters.",
    "priority": 0,
    "object_types": ["Shape"],
    "logical_expression": {
        "logical_operator": "and",
        "logical_expressions": [
            {
                "criterion": "x",
                "operator": "==",
                "comparison_value": 1.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "y",
                "operator": "==",
                "comparison_value": 2.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "x",
                "operator": ">=",
                "comparison_value": 1.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "y",
                "operator": ">=",
                "comparison_value": 2.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "x",
                "operator": "<=",
                "comparison_value": 1.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "y",
                "operator": "<=",
                "comparison_value": 2.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "x",
                "operator": "!=",
                "comparison_value": 99.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            {
                "criterion": "y",
                "operator": "!=",
                "comparison_value": 99.0000001,
                "parameters": [],
                "multi_value_behavior": "none"
            }
        ]
    }
}

MIXED_FILTER = {
    "name": "Mixed Type Filter",
    "description": "Used to determine whether Shapes and Points can be filtered together.",
    "priority": 1,
    "object_types": ["Shape", "Point"],
    "logical_expression": {
        "logical_operator": "and",
        "logical_expressions": [
            {
                "criterion": "x",
                "operator": ">=",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "each_meets_criterion"
            },
            {
                "criterion": "y",
                "operator": ">=",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "each_meets_criterion"
            },
            {
                "criterion": "area",
                "operator": ">=",
                "comparison_value": 0,
                "parameters": [],
                "multi_value_behavior": "each_meets_criterion"
            },
            {
                "criterion": "volume",
                "operator": "==",
                "comparison_value": 0,
                "parameters": [0],
                "multi_value_behavior": "each_meets_criterion"
            }
        ]
    }
}

RULE_CLASS_EQ = {
    "criterion": "$CLASS$",
    "operator": "==",
    "comparison_value": "Shape",
    "parameters": [],
    "multi_value_behavior": "none"
}

RULE_CLASS_NEQ = {
    "criterion": "$CLASS$",
    "operator": "!=",
    "comparison_value": "Point",
    "parameters": [],
    "multi_value_behavior": "none"
}

RULE_CLASS_INVALID_OP = {
    "criterion": "$CLASS$",
    "operator": ">",
    "comparison_value": "Shape",
    "parameters": [],
    "multi_value_behavior": "none"
}

CLASS_FILTER = {
    "name": "Class Filter",
    "description": "Filters by class name.",
    "priority": 0,
    "object_types": ["Shape"],
    "logical_expression": {
        "criterion": "$CLASS$",
        "operator": "==",
        "comparison_value": "Shape",
        "parameters": [],
        "multi_value_behavior": "none"
    }
}

# Only check area >= 4 if the object is a Shape; otherwise pass automatically
CLASS_CONDITIONAL = {
    "if": {
        "criterion": "$CLASS$",
        "operator": "==",
        "comparison_value": "Shape",
        "parameters": [],
        "multi_value_behavior": "none"
    },
    "then": {
        "criterion": "area",
        "operator": ">=",
        "comparison_value": 4,
        "parameters": [],
        "multi_value_behavior": "none"
    },
    "else": True
}

CLASS_CONDITIONAL_FILTER = {
    "name": "Class Conditional Filter",
    "description": "Only checks area for Shapes. Points always pass.",
    "priority": 0,
    "object_types": ["Shape", "Point"],
    "logical_expression": CLASS_CONDITIONAL
}

HIGH_X_FILTER = object_filtering.ObjectFilter(
    name="High X",
    description="Checks for a high x value.",
    priority=0,
    logical_expression=object_filtering.Rule(
        criterion="x",
        operator=">=",
        comparison_value=10,
        multi_value_behavior="none"
    )
)

HIGH_Y_FILTER = object_filtering.ObjectFilter(
    name="High Y",
    description="Checks for a high y value.",
    priority=1,
    logical_expression=object_filtering.Rule(
        criterion="y",
        operator=">=",
        comparison_value=10,
        multi_value_behavior="none"
    )
)

LOW_Y_FILTER = object_filtering.ObjectFilter(
    name="Low Y",
    description="Checks for a low y value.",
    priority=1,
    logical_expression=object_filtering.Rule(
        criterion="y",
        operator="<",
        comparison_value=10,
        multi_value_behavior="none"
    )
)

class TestObjectWrapper(unittest.TestCase):
    def test_multiple_objects(self):
        wrapper = object_filtering.ObjectWrapper([SHAPE_1, SHAPE_2, SHAPE_3])

        assert object_filtering.type_name_matches(wrapper, "Shape")
        assert wrapper.x == [1, 2, 3]
        assert wrapper.y == [2, 4, 6]
        assert wrapper.area() == [2, 8, 18]
        assert wrapper.volume(3) == [6, 24, 54]

    def test_single_object(self):
        single_wrapper = object_filtering.ObjectWrapper(SHAPE_1)
        
        assert object_filtering.type_name_matches(single_wrapper, "Shape")
        assert single_wrapper.x == 1
        assert single_wrapper.y == 2
        assert single_wrapper.area() == 2
        assert single_wrapper.volume(3) == 6

class TestLogicalExpressionValidity(unittest.TestCase):
    def test_rule(self):
        assert object_filtering.is_rule_valid(RULE_X, SHAPE_BIG)
        assert object_filtering.is_rule_valid(RULE_Y, SHAPE_BIG)
        assert object_filtering.is_rule_valid(RULE_VOLUME, SHAPE_BIG)
        with pytest.raises(object_filtering.FilterError):
            object_filtering.is_rule_valid(RULE_SECRET, SHAPE_BIG)  # not decorated with @object_filtering.filter_criterion

    def test_conditional(self):
        assert object_filtering.is_conditional_expression_valid(CONDITIONAL_1, SHAPE_BIG)
        assert object_filtering.is_conditional_expression_valid(CONDITIONAL_2, SHAPE_BIG)

    def test_group(self):
        assert object_filtering.is_group_expression_valid(GROUP_1, SHAPE_BIG)
        assert object_filtering.is_group_expression_valid(GROUP_2, SHAPE_BIG)

    def test_logical(self):
        logical_expressions = [RULE_X, RULE_Y, RULE_AREA, RULE_VOLUME, CONDITIONAL_1, CONDITIONAL_2, GROUP_1, GROUP_2]
        for exp in logical_expressions:
            assert object_filtering.is_logical_expression_valid(exp, SHAPE_BIG)
        with pytest.raises(object_filtering.FilterError):
            object_filtering.is_logical_expression_valid(RULE_SECRET, SHAPE_BIG)

class TestLogicalExpressionResult(unittest.TestCase):
    def test_rule(self):
        assert object_filtering.execute_rule_on_object(SHAPE_BIG, RULE_X)
        assert object_filtering.execute_rule_on_object(SHAPE_BIG, RULE_Y)
        assert object_filtering.execute_rule_on_object(SHAPE_BIG, RULE_VOLUME)
        with pytest.raises(AttributeError):
            object_filtering.execute_rule_on_object(SHAPE_BIG, RULE_SECRET)  # not decorated with @object_filtering.filter_criterion

    def test_conditional(self):
        assert object_filtering.execute_conditional_expression_on_object(SHAPE_BIG, CONDITIONAL_1)
        assert object_filtering.execute_conditional_expression_on_object(SHAPE_BIG, CONDITIONAL_2)

    def test_group(self):
        assert object_filtering.execute_group_expression_on_object(SHAPE_BIG, GROUP_1)
        assert object_filtering.execute_group_expression_on_object(SHAPE_BIG, GROUP_2)

    def test_logical(self):
        logical_expressions = [RULE_X, RULE_Y, RULE_AREA, RULE_VOLUME, CONDITIONAL_1, CONDITIONAL_2, GROUP_1, GROUP_2]
        for exp in logical_expressions:
            assert object_filtering.execute_logical_expression_on_object(SHAPE_BIG, exp)
        with pytest.raises(AttributeError):
            object_filtering.execute_logical_expression_on_object(SHAPE_BIG, RULE_SECRET)

class TestFilter(unittest.TestCase):
    def test_group_filters(self):
        for shape_filter in (SHAPE_FILTER_1, SHAPE_FILTER_2):
            assert object_filtering.execute_filter_on_object(SHAPE_BIG, shape_filter)
            assert object_filtering.execute_filter_on_object(SHAPE_MEDIUM, shape_filter)
            assert not object_filtering.execute_filter_on_object(SHAPE_SMALL, shape_filter)
            
    def test_conditional_filters(self):
        for shape_filter in (SHAPE_FILTER_3, SHAPE_FILTER_4):
            assert object_filtering.execute_filter_on_object(SHAPE_BIG, shape_filter)
            assert object_filtering.execute_filter_on_object(SHAPE_MEDIUM, shape_filter)
            assert not object_filtering.execute_filter_on_object(SHAPE_SMALL, shape_filter)
            
    def test_simple_filter(self):
        assert object_filtering.execute_filter_on_object(SHAPE_BIG, SHAPE_FILTER_5)
        assert object_filtering.execute_filter_on_object(SHAPE_MEDIUM, SHAPE_FILTER_5)
        assert not object_filtering.execute_filter_on_object(SHAPE_SMALL, SHAPE_FILTER_5)
            
    def test_nested_filter(self):
        assert object_filtering.execute_filter_on_object(SHAPE_BIG, SHAPE_FILTER_6)
        assert object_filtering.execute_filter_on_object(SHAPE_MEDIUM, SHAPE_FILTER_6)
        assert not object_filtering.execute_filter_on_object(SHAPE_SMALL, SHAPE_FILTER_6)
    
    def test_filter_with_single_wrapper(self):
        wrapper = object_filtering.ObjectWrapper(SHAPE_1)

        assert object_filtering.is_filter_valid(SHAPE_FILTER_1, wrapper)
        assert object_filtering.is_filter_valid(SHAPE_FILTER_2, wrapper)
        assert object_filtering.is_filter_valid(SHAPE_FILTER_3, wrapper)
        assert object_filtering.is_filter_valid(SHAPE_FILTER_4, wrapper)
        assert object_filtering.is_filter_valid(SHAPE_FILTER_5, wrapper)
        assert object_filtering.is_filter_valid(SHAPE_FILTER_6, wrapper)
    
    def test_filter_with_multi_wrapper(self):
        wrapper = object_filtering.ObjectWrapper([SHAPE_1, SHAPE_2, SHAPE_3])

        assert object_filtering.execute_filter_on_object(wrapper, SHAPE_FILTER_1)
        assert object_filtering.execute_filter_on_object(wrapper, SHAPE_FILTER_2)
        assert object_filtering.execute_filter_on_object(wrapper, SHAPE_FILTER_3)
        assert object_filtering.execute_filter_on_object(wrapper, SHAPE_FILTER_4)
        assert object_filtering.execute_filter_on_object(wrapper, SHAPE_FILTER_5)
        assert object_filtering.execute_filter_on_object(wrapper, SHAPE_FILTER_6)
    
    def test_filter_with_multi_wrapper_2(self):
        wrapper = object_filtering.ObjectWrapper([SHAPE_2, SHAPE_2])

        with pytest.raises(ValueError):
            object_filtering.execute_rule_on_object(wrapper, RULE_MULTI_NONE)
        assert object_filtering.execute_rule_on_object(wrapper, RULE_MULTI_ADD)
        assert object_filtering.execute_rule_on_object(wrapper, RULE_MULTI_MEET)
        assert object_filtering.execute_rule_on_object(wrapper, RULE_MULTI_EQUAL)

    def test_float_comparison(self):
        shape_float_1 = Shape(1.0000002, 2)
        assert object_filtering.execute_filter_on_object(shape_float_1, SHAPE_FILTER_FLOAT)

class TestLogicalExpressionClasses(unittest.TestCase):
    def test_init(self):
        object_filter = object_filtering.ObjectFilter("test", "test description", 0, ["object"], True)
        assert isinstance(object_filter, object_filtering.ObjectFilter)
        assert isinstance(object_filter, object_filtering.LogicalExpression)
        assert object_filtering.execute_filter_on_object("test", object_filter)
        assert {"object_filter": object_filter}

        rule = object_filtering.Rule("area", "==", 2, [], "none")
        assert isinstance(rule, object_filtering.Rule)
        assert isinstance(rule, object_filtering.LogicalExpression)
        assert object_filtering.execute_rule_on_object(SHAPE_1, rule)
        assert {"rule": rule}

        group_expression = object_filtering.GroupExpression("or", [True, False])
        assert isinstance(group_expression, object_filtering.GroupExpression)
        assert isinstance(group_expression, object_filtering.LogicalExpression)
        assert object_filtering.execute_group_expression_on_object("test", group_expression)
        assert {"group_expression": group_expression}

        conditional_expression = object_filtering.ConditionalExpression(False, False, True)
        assert isinstance(conditional_expression, object_filtering.ConditionalExpression)
        assert isinstance(conditional_expression, object_filtering.LogicalExpression)
        assert object_filtering.execute_conditional_expression_on_object("test", conditional_expression)
        assert {"conditional_expression": conditional_expression}

    def test_dot_notation_read(self):
        rule = object_filtering.Rule("area", "==", 2, [], "none")
        assert rule.criterion == "area"
        assert rule.operator == "=="
        assert rule.comparison_value == 2
        assert rule.parameters == []
        assert rule.multi_value_behavior == "none"

        object_filter = object_filtering.ObjectFilter("test", "desc", 0, ["object"], True)
        assert object_filter.name == "test"
        assert object_filter.description == "desc"
        assert object_filter.priority == 0
        assert object_filter.object_types == ["object"]
        assert object_filter.logical_expression == True

        group = object_filtering.GroupExpression("and", [True])
        assert group.logical_operator == "and"
        assert group.logical_expressions == [True]

        cond = object_filtering.ConditionalExpression(True, False, True)
        assert cond._if == True
        assert cond._then == False
        assert cond._else == True

    def test_dot_notation_write(self):
        rule = object_filtering.Rule("area", "==", 2, [], "none")
        rule.criterion = "x"
        assert rule["criterion"] == "x"
        assert rule.criterion == "x"

        object_filter = object_filtering.ObjectFilter("test", "desc", 0, ["object"], True)
        object_filter.name = "updated"
        assert object_filter["name"] == "updated"

        cond = object_filtering.ConditionalExpression(True, False, True)
        cond._if = False
        assert cond["if"] == False

    def test_invalid_key_bracket(self):
        rule = object_filtering.Rule()
        with pytest.raises(KeyError):
            rule["bad_key"] = 123

        object_filter = object_filtering.ObjectFilter()
        with pytest.raises(KeyError):
            object_filter["unknown"] = "value"

        group = object_filtering.GroupExpression()
        with pytest.raises(KeyError):
            group["extra"] = True

        cond = object_filtering.ConditionalExpression()
        with pytest.raises(KeyError):
            cond["when"] = True

    def test_invalid_key_dot(self):
        rule = object_filtering.Rule()
        with pytest.raises(AttributeError):
            rule.bad_key = 123

        with pytest.raises(AttributeError):
            _ = rule.nonexistent

    def test_delete_key(self):
        rule = object_filtering.Rule()
        with pytest.raises(TypeError):
            del rule["criterion"]

    def test_invalid_attribute_read(self):
        group = object_filtering.GroupExpression()
        with pytest.raises(AttributeError):
            _ = group.nonexistent

    def test_rule_from_dict(self):
        d = {"criterion": "area", "operator": ">=", "comparison_value": 4,
             "parameters": [], "multi_value_behavior": "none"}
        rule = object_filtering.Rule.from_dict(d)
        assert isinstance(rule, object_filtering.Rule)
        assert rule.criterion == "area"
        assert rule.operator == ">="
        assert rule.comparison_value == 4

    def test_rule_from_dict_invalid_operator(self):
        d = {"criterion": "area", "operator": "~", "comparison_value": 4,
             "parameters": [], "multi_value_behavior": "none"}
        with pytest.raises(ValueError):
            object_filtering.Rule.from_dict(d)

    def test_rule_from_dict_invalid_multi_value_behavior(self):
        d = {"criterion": "area", "operator": "==", "comparison_value": 4,
             "parameters": [], "multi_value_behavior": "bad"}
        with pytest.raises(ValueError):
            object_filtering.Rule.from_dict(d)

    def test_rule_from_dict_extra_key(self):
        d = {"criterion": "area", "operator": "==", "comparison_value": 4,
             "parameters": [], "multi_value_behavior": "none", "extra": True}
        with pytest.raises(KeyError):
            object_filtering.Rule.from_dict(d)

    def test_rule_from_dict_missing_key(self):
        d = {"criterion": "area", "operator": "=="}
        with pytest.raises(KeyError):
            object_filtering.Rule.from_dict(d)

    def test_group_expression_from_dict(self):
        d = {"logical_operator": "and", "logical_expressions": [
            {"criterion": "x", "operator": ">=", "comparison_value": 2,
             "parameters": [], "multi_value_behavior": "none"},
            True
        ]}
        group = object_filtering.GroupExpression.from_dict(d)
        assert isinstance(group, object_filtering.GroupExpression)
        assert isinstance(group.logical_expressions[0], object_filtering.Rule)
        assert group.logical_expressions[1] is True

    def test_group_expression_from_dict_invalid_operator(self):
        d = {"logical_operator": "xor", "logical_expressions": [True]}
        with pytest.raises(ValueError):
            object_filtering.GroupExpression.from_dict(d)

    def test_conditional_expression_from_dict(self):
        d = {"if": {"criterion": "x", "operator": ">=", "comparison_value": 1,
                     "parameters": [], "multi_value_behavior": "none"},
             "then": True, "else": False}
        cond = object_filtering.ConditionalExpression.from_dict(d)
        assert isinstance(cond, object_filtering.ConditionalExpression)
        assert isinstance(cond["if"], object_filtering.Rule)
        assert cond["then"] is True
        assert cond["else"] is False

    def test_rule_init_invalid_criterion(self):
        with pytest.raises(TypeError):
            object_filtering.Rule(criterion=123, operator="==", comparison_value=1, parameters=[], multi_value_behavior="none")

    def test_rule_init_invalid_operator(self):
        with pytest.raises(ValueError):
            object_filtering.Rule(criterion="x", operator="~", comparison_value=1, parameters=[], multi_value_behavior="none")

    def test_rule_init_invalid_parameters(self):
        with pytest.raises(TypeError):
            object_filtering.Rule(criterion="x", operator="==", comparison_value=1, parameters="not a list", multi_value_behavior="none")

    def test_rule_init_invalid_multi_value_behavior(self):
        with pytest.raises(ValueError):
            object_filtering.Rule(criterion="x", operator="==", comparison_value=1, parameters=[], multi_value_behavior="bad")

    def test_group_expression_init_invalid_operator(self):
        with pytest.raises(ValueError):
            object_filtering.GroupExpression(logical_operator="xor", logical_expressions=[True])

    def test_group_expression_init_invalid_expressions_type(self):
        with pytest.raises(TypeError):
            object_filtering.GroupExpression(logical_operator="and", logical_expressions="not a list")

    def test_group_expression_init_invalid_expression_element(self):
        with pytest.raises(TypeError):
            object_filtering.GroupExpression(logical_operator="and", logical_expressions=[42])

    def test_object_filter_init_invalid_name(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(name=123, description="desc", priority=0, object_types=["obj"], logical_expression=True)

    def test_object_filter_init_invalid_description(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(name="test", description=123, priority=0, object_types=["obj"], logical_expression=True)

    def test_object_filter_init_invalid_priority(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(name="test", description="desc", priority="zero", object_types=["obj"], logical_expression=True)

    def test_object_filter_init_invalid_object_types_not_list(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(name="test", description="desc", priority=0, object_types="Shape", logical_expression=True)

    def test_object_filter_init_invalid_object_types_elements(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(name="test", description="desc", priority=0, object_types=[123], logical_expression=True)

    def test_object_filter_init_invalid_logical_expression(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(name="test", description="desc", priority=0, object_types=["obj"], logical_expression="not valid")

    def test_object_filter_init_invalid_logical_expression_dict(self):
        with pytest.raises(TypeError):
            object_filtering.ObjectFilter(
                name="test",
                description="desc",
                priority=0,
                object_types=["obj"],
                logical_expression={
                    "criterion": "x",
                    "operator": "==",
                    "comparison_value": 1,
                    "parameters": [],
                    "multi_value_behavior": "none"
                }
            )

    def test_conditional_expression_init_invalid_if(self):
        with pytest.raises(TypeError):
            object_filtering.ConditionalExpression(_if="not a bool", _then=True, _else=True)

    def test_conditional_expression_init_invalid_then(self):
        with pytest.raises(TypeError):
            object_filtering.ConditionalExpression(_if=True, _then=42, _else=True)

    def test_conditional_expression_init_invalid_else(self):
        with pytest.raises(TypeError):
            object_filtering.ConditionalExpression(_if=True, _then=True, _else=[1, 2])

    def test_conditional_expression_init_invalid_if_dict(self):
        with pytest.raises(TypeError):
            object_filtering.ConditionalExpression(
                _if={"criterion": "x", "operator": ">=", "comparison_value": 1,
                     "parameters": [], "multi_value_behavior": "none"},
                _then=True,
                _else=True
            )

    def test_conditional_expression_init_invalid_then_dict(self):
        with pytest.raises(TypeError):
            object_filtering.ConditionalExpression(
                _if=True,
                _then={"if": True, "then": False, "else": True},
                _else=True
            )

    def test_conditional_expression_init_invalid_else_dict(self):
        with pytest.raises(TypeError):
            object_filtering.ConditionalExpression(
                _if=True,
                _then=True,
                _else={"logical_operator": "and", "logical_expressions": [True]}
            )

    def test_conditional_expression_init_valid_logical_expressions(self):
        rule = object_filtering.Rule("x", ">=", 1, [], "none")
        group = object_filtering.GroupExpression("and", [True])
        inner_cond = object_filtering.ConditionalExpression(True, False, True)
        cond = object_filtering.ConditionalExpression(
            _if=rule, _then=group, _else=inner_cond
        )
        assert isinstance(cond["if"], object_filtering.Rule)
        assert isinstance(cond["then"], object_filtering.GroupExpression)
        assert isinstance(cond["else"], object_filtering.ConditionalExpression)

    def test_object_filter_from_dict(self):
        d = {
            "name": "Test Filter",
            "description": "A test",
            "priority": 0,
            "object_types": ["Shape"],
            "logical_expression": {
                "logical_operator": "and",
                "logical_expressions": [
                    {
                        "criterion": "x",
                        "operator": ">=",
                        "comparison_value": 2,
                        "parameters": [],
                        "multi_value_behavior": "none"
                    },
                    {
                        "if": {
                            "criterion": "y",
                            "operator": ">=",
                            "comparison_value": 1,
                            "parameters": [],
                            "multi_value_behavior": "none"
                        },
                        "then": True,
                        "else": False
                    }
                ]
            }
        }
        f = object_filtering.ObjectFilter.from_dict(d)
        assert isinstance(f, object_filtering.ObjectFilter)
        assert f.name == "Test Filter"
        group = f.logical_expression
        assert isinstance(group, object_filtering.GroupExpression)
        assert isinstance(group.logical_expressions[0], object_filtering.Rule)
        assert isinstance(group.logical_expressions[1], object_filtering.ConditionalExpression)

    def test_logical_expression_from_dict_passthrough(self):
        rule = object_filtering.Rule("x", "==", 1, [], "none")
        result = object_filtering.logical_expression_from_dict(rule)
        assert result is rule

    def test_logical_expression_from_dict_bool(self):
        assert object_filtering.logical_expression_from_dict(True) is True
        assert object_filtering.logical_expression_from_dict(False) is False

    def test_logical_expression_from_dict_invalid_type(self):
        with pytest.raises(TypeError):
            object_filtering.logical_expression_from_dict(42)

    def test_isinstance_rule(self):
        rule = object_filtering.Rule("area", "==", 2, [], "none")
        assert isinstance(rule, object_filtering.Rule)
        assert isinstance(rule, object_filtering._LogicalExpressionBase)
        assert isinstance(rule, dict)

    def test_isinstance_group_expression(self):
        group = object_filtering.GroupExpression("and", [True])
        assert isinstance(group, object_filtering.GroupExpression)
        assert isinstance(group, object_filtering._LogicalExpressionBase)
        assert isinstance(group, dict)

    def test_isinstance_conditional_expression(self):
        cond = object_filtering.ConditionalExpression(True, False, True)
        assert isinstance(cond, object_filtering.ConditionalExpression)
        assert isinstance(cond, object_filtering._LogicalExpressionBase)
        assert isinstance(cond, dict)

    def test_isinstance_object_filter(self):
        f = object_filtering.ObjectFilter("test", "desc", 0, ["obj"], True)
        assert isinstance(f, object_filtering.ObjectFilter)
        assert isinstance(f, object_filtering._LogicalExpressionBase)
        assert isinstance(f, dict)

    def test_isinstance_bool_not_base(self):
        assert not isinstance(True, object_filtering._LogicalExpressionBase)
        assert not isinstance(False, object_filtering._LogicalExpressionBase)

    def test_subclass_hierarchy(self):
        assert issubclass(object_filtering.Rule, object_filtering._LogicalExpressionBase)
        assert issubclass(object_filtering.GroupExpression, object_filtering._LogicalExpressionBase)
        assert issubclass(object_filtering.ConditionalExpression, object_filtering._LogicalExpressionBase)
        assert issubclass(object_filtering.ObjectFilter, object_filtering._LogicalExpressionBase)
        assert not issubclass(bool, object_filtering._LogicalExpressionBase)

    def test_dict_with_rule_criteria_is_not_rule(self):
        d = {
            "criterion": "area",
            "operator": ">=",
            "comparison_value": 4,
            "parameters": [],
            "multi_value_behavior": "none"
        }
        assert not isinstance(d, object_filtering.Rule)
        assert not isinstance(d, object_filtering._LogicalExpressionBase)
        assert object_filtering.get_logical_expression_type(d) is object_filtering.Rule

    def test_dict_with_group_criteria_is_not_group(self):
        d = {
            "logical_operator": "and",
            "logical_expressions": [True]
        }
        assert not isinstance(d, object_filtering.GroupExpression)
        assert not isinstance(d, object_filtering._LogicalExpressionBase)
        assert object_filtering.get_logical_expression_type(d) is object_filtering.GroupExpression

    def test_dict_with_conditional_criteria_is_not_conditional(self):
        d = {
            "if": True,
            "then": True,
            "else": False
        }
        assert not isinstance(d, object_filtering.ConditionalExpression)
        assert not isinstance(d, object_filtering._LogicalExpressionBase)
        assert object_filtering.get_logical_expression_type(d) is object_filtering.ConditionalExpression

    def test_dict_with_object_filter_criteria_is_not_object_filter(self):
        d = {
            "name": "test",
            "description": "desc",
            "priority": 0,
            "object_types": ["obj"],
            "logical_expression": True
        }
        assert not isinstance(d, object_filtering.ObjectFilter)
        assert not isinstance(d, object_filtering._LogicalExpressionBase)
        assert object_filtering.get_logical_expression_type(d) is object_filtering.ObjectFilter

class TestDictToLogicalExpression(unittest.TestCase):
    def test_dict_to_rule(self):
        d = {
            "criterion": "area",
            "operator": ">=",
            "comparison_value": 4,
            "parameters": [],
            "multi_value_behavior": "none"
        }
        result = object_filtering.dict_to_logical_expression(d)
        assert isinstance(result, object_filtering.Rule)
        assert result.criterion == "area"
        assert result.operator == ">="
        assert result.comparison_value == 4

    def test_dict_to_group_expression(self):
        d = {
            "logical_operator": "and",
            "logical_expressions": [
                {
                    "criterion": "x",
                    "operator": ">=",
                    "comparison_value": 2,
                    "parameters": [],
                    "multi_value_behavior": "none"
                },
                True
            ]
        }
        result = object_filtering.dict_to_logical_expression(d)
        assert isinstance(result, object_filtering.GroupExpression)
        assert result.logical_operator == "and"
        assert isinstance(result.logical_expressions[0], object_filtering.Rule)
        assert result.logical_expressions[1] is True

    def test_dict_to_conditional_expression(self):
        d = {
            "if": {
                "criterion": "x",
                "operator": ">=",
                "comparison_value": 1,
                "parameters": [],
                "multi_value_behavior": "none"
            },
            "then": True,
            "else": False
        }
        result = object_filtering.dict_to_logical_expression(d)
        assert isinstance(result, object_filtering.ConditionalExpression)
        assert isinstance(result["if"], object_filtering.Rule)
        assert result["then"] is True
        assert result["else"] is False

    def test_dict_to_object_filter(self):
        d = {
            "name": "Test",
            "description": "desc",
            "priority": 0,
            "object_types": ["Shape"],
            "logical_expression": True
        }
        result = object_filtering.dict_to_logical_expression(d)
        assert isinstance(result, object_filtering.ObjectFilter)
        assert result.name == "Test"
        assert result.logical_expression is True

    def test_dict_to_object_filter_nested(self):
        d = {
            "name": "Nested",
            "description": "desc",
            "priority": 1,
            "object_types": ["Shape"],
            "logical_expression": {
                "logical_operator": "or",
                "logical_expressions": [
                    {
                        "criterion": "x",
                        "operator": "==",
                        "comparison_value": 1,
                        "parameters": [],
                        "multi_value_behavior": "none"
                    },
                    {
                        "if": True,
                        "then": False,
                        "else": True
                    }
                ]
            }
        }
        result = object_filtering.dict_to_logical_expression(d)
        assert isinstance(result, object_filtering.ObjectFilter)
        group = result.logical_expression
        assert isinstance(group, object_filtering.GroupExpression)
        assert isinstance(group.logical_expressions[0], object_filtering.Rule)
        assert isinstance(group.logical_expressions[1], object_filtering.ConditionalExpression)

    def test_invalid_keys_raises_value_error(self):
        d = {
            "foo": "bar",
            "baz": 123
        }
        with pytest.raises(ValueError):
            object_filtering.dict_to_logical_expression(d)

    def test_empty_dict_raises_value_error(self):
        with pytest.raises(ValueError):
            object_filtering.dict_to_logical_expression({})

class TestImplicitDictConversion(unittest.TestCase):
    """Tests that plain dicts are implicitly converted to LogicalExpression
    types when passed into functions, without mutating the original dict."""

    RULE_DICT = {
        "criterion": "area",
        "operator": "==",
        "comparison_value": 2,
        "parameters": [],
        "multi_value_behavior": "none"
    }
    GROUP_DICT = {
        "logical_operator": "and",
        "logical_expressions": [
            {
                "criterion": "area",
                "operator": "==",
                "comparison_value": 2,
                "parameters": [],
                "multi_value_behavior": "none"
            }
        ]
    }
    COND_DICT = {
        "if": {
            "criterion": "area",
            "operator": "==",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "none"
        },
        "then": True,
        "else": False
    }
    FILTER_DICT = {
        "name": "test",
        "description": "test",
        "priority": 0,
        "object_types": ["Shape"],
        "logical_expression": {
            "criterion": "area",
            "operator": "==",
            "comparison_value": 2,
            "parameters": [],
            "multi_value_behavior": "none"
        }
    }

    def _assert_still_plain_dict(self, d):
        assert type(d) is dict

    def test_execute_logical_expression_on_object_with_dict(self):
        d = dict(self.RULE_DICT)
        assert object_filtering.execute_logical_expression_on_object(SHAPE_1, d)
        self._assert_still_plain_dict(d)

    def test_execute_rule_on_object_with_dict(self):
        d = dict(self.RULE_DICT)
        assert object_filtering.execute_rule_on_object(SHAPE_1, d)
        self._assert_still_plain_dict(d)

    def test_execute_conditional_expression_on_object_with_dict(self):
        d = {
            "if": dict(self.RULE_DICT),
            "then": True,
            "else": False
        }
        assert object_filtering.execute_conditional_expression_on_object(SHAPE_1, d)
        self._assert_still_plain_dict(d)

    def test_execute_group_expression_on_object_with_dict(self):
        d = {
            "logical_operator": "and",
            "logical_expressions": [dict(self.RULE_DICT)]
        }
        assert object_filtering.execute_group_expression_on_object(SHAPE_1, d)
        self._assert_still_plain_dict(d)

    def test_execute_filter_on_object_with_dict(self):
        d = dict(self.FILTER_DICT)
        assert object_filtering.execute_filter_on_object(SHAPE_1, d)
        self._assert_still_plain_dict(d)

    def test_is_logical_expression_valid_with_dict(self):
        d = dict(self.RULE_DICT)
        assert object_filtering.is_logical_expression_valid(d, SHAPE_1)
        self._assert_still_plain_dict(d)

    def test_is_rule_valid_with_dict(self):
        d = dict(self.RULE_DICT)
        assert object_filtering.is_rule_valid(d, SHAPE_1)
        self._assert_still_plain_dict(d)

    def test_is_conditional_expression_valid_with_dict(self):
        d = {
            "if": dict(self.RULE_DICT),
            "then": True,
            "else": False
        }
        assert object_filtering.is_conditional_expression_valid(d, SHAPE_1)
        self._assert_still_plain_dict(d)

    def test_is_group_expression_valid_with_dict(self):
        d = {
            "logical_operator": "and",
            "logical_expressions": [dict(self.RULE_DICT)]
        }
        assert object_filtering.is_group_expression_valid(d, SHAPE_1)
        self._assert_still_plain_dict(d)

    def test_is_filter_valid_with_dict(self):
        d = dict(self.FILTER_DICT)
        assert object_filtering.is_filter_valid(d, SHAPE_1)
        self._assert_still_plain_dict(d)

    def test_get_value_with_dict(self):
        d = dict(self.RULE_DICT)
        assert object_filtering.get_value(SHAPE_1, d) == 2
        self._assert_still_plain_dict(d)

    def test_sanitize_filter_with_dict(self):
        d = dict(self.FILTER_DICT)
        result = object_filtering.sanitize_filter(d)
        self._assert_still_plain_dict(d)
        assert isinstance(result, dict)

    def test_sort_filter_list_with_dicts(self):
        d1 = dict(self.FILTER_DICT)
        d2 = {
            **self.FILTER_DICT,
            "priority": 1,
            "name": "another"
        }
        result = object_filtering.sort_filter_list([d2, d1])
        self._assert_still_plain_dict(d1)
        self._assert_still_plain_dict(d2)
        assert result[0]["name"] == "test"

    def test_execute_filter_on_object_invalid_dict_raises_value_error(self):
        d = {
            "foo": "bar",
            "baz": 123
        }
        with pytest.raises(ValueError):
            object_filtering.execute_filter_on_object(SHAPE_1, d)

    def test_execute_rule_on_object_invalid_dict_raises_value_error(self):
        d = {
            "foo": "bar",
            "baz": 123
        }
        with pytest.raises(ValueError):
            object_filtering.execute_rule_on_object(SHAPE_1, d)

    def test_is_logical_expression_valid_invalid_dict_raises_value_error(self):
        d = {
            "foo": "bar",
            "baz": 123
        }
        with pytest.raises(ValueError):
            object_filtering.is_logical_expression_valid(d)


class TestMixedTypeFilters(unittest.TestCase):
    def test_mixed_type_filter(self):
        shape = Shape(2, 2)
        point = Point(2, 2)
        wrapper = object_filtering.ObjectWrapper([shape, point])

        assert object_filtering.type_name_matches(wrapper, MIXED_FILTER["object_types"])
        assert object_filtering.is_filter_valid(MIXED_FILTER, wrapper)
        assert object_filtering.execute_filter_on_object(wrapper, MIXED_FILTER)

class TestFilterList(unittest.TestCase):
    def test_filter_list_get_first_success(self):
        shape_1 = Shape(10, 0)
        shape_2 = Shape(0, 10)
        shape_3 = Shape(0, 0)
        filter_list = [HIGH_X_FILTER, HIGH_Y_FILTER]
        assert object_filtering.execute_filter_list_on_object_get_first_success(shape_1, filter_list) == "High X"
        assert object_filtering.execute_filter_list_on_object_get_first_success(shape_2, filter_list) == "High Y"
        with pytest.raises(ValueError):
            object_filtering.execute_filter_list_on_object_get_first_success(shape_3, filter_list)

    def test_sort_filter_list(self):
        filter_list = [LOW_Y_FILTER, HIGH_Y_FILTER, HIGH_X_FILTER]
        filter_list = object_filtering.sort_filter_list(filter_list)
        assert filter_list == [HIGH_X_FILTER, HIGH_Y_FILTER, LOW_Y_FILTER]

class TestClassVariable(unittest.TestCase):
    def test_class_variable_rule_validity(self):
        assert object_filtering.is_rule_valid(RULE_CLASS_EQ, SHAPE_BIG)
        assert object_filtering.is_rule_valid(RULE_CLASS_NEQ, SHAPE_BIG)
        with pytest.raises(object_filtering.FilterError):
            object_filtering.is_rule_valid(RULE_CLASS_INVALID_OP, SHAPE_BIG)

    def test_class_variable_invalid_operators(self):
        for op in ("<", "<=", ">=", ">"):
            rule = {
                "criterion": "$CLASS$",
                "operator": op,
                "comparison_value": "Shape",
                "parameters": [],
                "multi_value_behavior": "none"
            }
            with pytest.raises(object_filtering.FilterError):
                object_filtering.is_rule_valid(rule, SHAPE_BIG)

    def test_class_variable_rule_execution(self):
        assert object_filtering.execute_rule_on_object(SHAPE_BIG, RULE_CLASS_EQ)
        assert object_filtering.execute_rule_on_object(SHAPE_BIG, RULE_CLASS_NEQ)
        point = Point(1, 1)
        assert not object_filtering.execute_rule_on_object(point, RULE_CLASS_EQ)
        assert not object_filtering.execute_rule_on_object(point, RULE_CLASS_NEQ)  # Point != "Point" is False

    def test_class_variable_filter(self):
        assert object_filtering.execute_filter_on_object(SHAPE_BIG, CLASS_FILTER)

    def test_class_variable_conditional(self):
        # Shape with area >= 4 passes the "then" branch
        assert object_filtering.execute_conditional_expression_on_object(SHAPE_BIG, CLASS_CONDITIONAL)
        # Shape with area < 4 (1*1=1) fails the "then" branch
        assert not object_filtering.execute_conditional_expression_on_object(SHAPE_SMALL, CLASS_CONDITIONAL)
        # Point takes the "else" branch (True), so always passes
        point = Point(0, 0)
        assert object_filtering.execute_conditional_expression_on_object(point, CLASS_CONDITIONAL)

    def test_class_variable_conditional_filter(self):
        assert object_filtering.execute_filter_on_object(SHAPE_BIG, CLASS_CONDITIONAL_FILTER)
        assert not object_filtering.execute_filter_on_object(SHAPE_SMALL, CLASS_CONDITIONAL_FILTER)
        point = Point(0, 0)
        assert object_filtering.execute_filter_on_object(point, CLASS_CONDITIONAL_FILTER)

    def test_class_variable_with_object_wrapper(self):
        wrapper = object_filtering.ObjectWrapper(SHAPE_1)
        assert object_filtering.get_value(wrapper, RULE_CLASS_EQ) == "Shape"

        multi_wrapper = object_filtering.ObjectWrapper([SHAPE_1, SHAPE_2])
        assert object_filtering.get_value(multi_wrapper, RULE_CLASS_EQ) == ["Shape", "Shape"]
