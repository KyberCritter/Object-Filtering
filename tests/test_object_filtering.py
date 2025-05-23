# (c) 2025 Scott Ratchford
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

if __name__ == '__main__':
    pytest.main()
