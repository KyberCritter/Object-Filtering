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

    @object_filtering.filter_criterion
    def area_if_stretched(self, x_2: int | float, y_2: int | float) -> int | float:
        return self.x * x_2 + self.y * y_2

    @object_filtering.filter_criterion
    def has_long_side(self, length: int | float) -> bool:
        return self.x > length or self.y > length

    def secret_method(self) -> None:
        return

large_filter = object_filtering.ObjectFilter(
    name="Shape Area",
    description="Determines whether Shape is large.",
    priority=0,
    object_types=["Shape",],
    logical_expression=object_filtering.GroupExpression(
        logical_operator="and",
        logical_expressions=[
            object_filtering.Rule(
                criterion="area",
                operator=">=",
                comparison_value=4,
                parameters=[],
                multi_value_behavior="none"
            ),
            object_filtering.Rule(
                criterion="volume",
                operator=">=",
                comparison_value=8,
                parameters=[2,],
                multi_value_behavior="none"
            ),
            object_filtering.GroupExpression(
                logical_operator="or",
                logical_expressions=[
                    object_filtering.Rule(
                        criterion="area_if_stretched",
                        operator=">=",
                        comparison_value=9,
                        parameters=[2, 3],
                        multi_value_behavior="none"
                    ),
                    object_filtering.Rule(
                        criterion="has_long_side",
                        operator=">=",
                        comparison_value=1,
                        parameters=[1,],
                        multi_value_behavior="none"
                    ),
                ]
            ),
        ]
    )
)

class TestNaturalLanguage(unittest.TestCase):
    def test_natural_language_explanation(self):
        expl = object_filtering.natural_language.explain_filter(large_filter)
        expected_expl = "Filter \"Shape Area\": Determines whether Shape is large.\n"
        expected_expl += "This filter applies to objects of type: Shape.\n"
        expected_expl += "All of the following conditions must be met:\n"
        expected_expl += "    - area is greater than or equal to 4.\n"
        expected_expl += "    - The result of calling volume with parameter 2 is greater than or equal to 8.\n"
        expected_expl += "    - At least one of the following conditions must be met:\n"
        expected_expl += "        - The result of calling area_if_stretched with parameters 2 and 3 is greater than or equal to 9.\n"
        expected_expl += "        - The result of calling has_long_side with parameter 1 is greater than or equal to 1."

        assert expl == expected_expl

class TestExplainExpressionBool(unittest.TestCase):
    def test_true(self):
        result = object_filtering.explain_expression(True)
        assert result == "This condition is always true."

    def test_false(self):
        result = object_filtering.explain_expression(False)
        assert result == "This condition is always false."

    def test_true_indented(self):
        result = object_filtering.explain_expression(True, depth=2)
        assert result == "        This condition is always true."

    def test_false_indented(self):
        result = object_filtering.explain_expression(False, depth=1)
        assert result == "    This condition is always false."

class TestExplainExpressionRule(unittest.TestCase):
    def test_no_parameters(self):
        rule = object_filtering.Rule(
            criterion="x", operator=">=", comparison_value=5,
            parameters=[], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "x is greater than or equal to 5."

    def test_single_parameter(self):
        rule = object_filtering.Rule(
            criterion="volume", operator="<", comparison_value=10,
            parameters=[3], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "The result of calling volume with parameter 3 is less than 10."

    def test_two_parameters(self):
        rule = object_filtering.Rule(
            criterion="area_if_stretched", operator="==", comparison_value=12,
            parameters=[2, 3], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "The result of calling area_if_stretched with parameters 2 and 3 equals 12."

    def test_three_parameters(self):
        rule = object_filtering.Rule(
            criterion="foo", operator="!=", comparison_value=0,
            parameters=[1, 2, 3], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "The result of calling foo with parameters 1, 2 and 3 does not equal 0."

    def test_all_operators(self):
        lines = []
        for op, phrase in [
            ("<", "is less than"),
            ("<=", "is less than or equal to"),
            ("==", "equals"),
            ("!=", "does not equal"),
            (">=", "is greater than or equal to"),
            (">", "is greater than"),
        ]:
            rule = object_filtering.Rule(
                criterion="x", operator=op, comparison_value=1,
                parameters=[], multi_value_behavior="none"
            )
            result = object_filtering.explain_expression(rule)
            lines.append(f"{op}: {result}")
            assert result == f"x {phrase} 1."

    def test_string_comparison_value(self):
        rule = object_filtering.Rule(
            criterion="name", operator="==", comparison_value="foo",
            parameters=[], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "name equals foo."

    def test_class_equals(self):
        rule = object_filtering.Rule(
            criterion="$CLASS$", operator="==", comparison_value="Shape",
            parameters=[], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "the object is a Shape."

    def test_class_not_equals(self):
        rule = object_filtering.Rule(
            criterion="$CLASS$", operator="!=", comparison_value="Point",
            parameters=[], multi_value_behavior="none"
        )
        result = object_filtering.explain_expression(rule)
        assert result == "the object is not a Point."

class TestExplainExpressionGroup(unittest.TestCase):
    def test_and_group(self):
        group = object_filtering.GroupExpression(
            logical_operator="and",
            logical_expressions=[
                object_filtering.Rule("x", ">=", 1, [], "none"),
                object_filtering.Rule("y", "<=", 10, [], "none"),
            ]
        )
        result = object_filtering.explain_expression(group)
        expected = (
            "All of the following conditions must be met:\n"
            "    - x is greater than or equal to 1.\n"
            "    - y is less than or equal to 10."
        )
        assert result == expected

    def test_or_group(self):
        group = object_filtering.GroupExpression(
            logical_operator="or",
            logical_expressions=[
                object_filtering.Rule("x", ">", 5, [], "none"),
                object_filtering.Rule("y", ">", 5, [], "none"),
            ]
        )
        result = object_filtering.explain_expression(group)
        expected = (
            "At least one of the following conditions must be met:\n"
            "    - x is greater than 5.\n"
            "    - y is greater than 5."
        )
        assert result == expected

    def test_group_with_bool(self):
        group = object_filtering.GroupExpression(
            logical_operator="and",
            logical_expressions=[True, False]
        )
        result = object_filtering.explain_expression(group)
        expected = (
            "All of the following conditions must be met:\n"
            "    - This condition is always true.\n"
            "    - This condition is always false."
        )
        assert result == expected

    def test_nested_groups(self):
        inner = object_filtering.GroupExpression(
            logical_operator="or",
            logical_expressions=[
                object_filtering.Rule("x", "==", 1, [], "none"),
                object_filtering.Rule("y", "==", 1, [], "none"),
            ]
        )
        outer = object_filtering.GroupExpression(
            logical_operator="and",
            logical_expressions=[
                object_filtering.Rule("area", ">", 0, [], "none"),
                inner,
            ]
        )
        result = object_filtering.explain_expression(outer)
        expected = (
            "All of the following conditions must be met:\n"
            "    - area is greater than 0.\n"
            "    - At least one of the following conditions must be met:\n"
            "        - x equals 1.\n"
            "        - y equals 1."
        )
        assert result == expected

class TestExplainExpressionConditional(unittest.TestCase):
    def test_simple_conditional(self):
        cond = object_filtering.ConditionalExpression(
            _if=object_filtering.Rule("x", ">=", 2, [], "none"),
            _then=object_filtering.Rule("y", ">=", 2, [], "none"),
            _else=False
        )
        result = object_filtering.explain_expression(cond)
        expected = (
            "If the following condition holds:\n"
            "    - x is greater than or equal to 2.\n"
            "Then:\n"
            "    - y is greater than or equal to 2.\n"
            "Otherwise:\n"
            "    - This condition is always false."
        )
        assert result == expected

    def test_conditional_with_bool_branches(self):
        cond = object_filtering.ConditionalExpression(
            _if=object_filtering.Rule("$CLASS$", "==", "Shape", [], "none"),
            _then=True,
            _else=False
        )
        result = object_filtering.explain_expression(cond)
        expected = (
            "If the following condition holds:\n"
            "    - the object is a Shape.\n"
            "Then:\n"
            "    - This condition is always true.\n"
            "Otherwise:\n"
            "    - This condition is always false."
        )
        assert result == expected

    def test_conditional_with_group_then(self):
        cond = object_filtering.ConditionalExpression(
            _if=object_filtering.Rule("$CLASS$", "==", "Shape", [], "none"),
            _then=object_filtering.GroupExpression("and", [
                object_filtering.Rule("x", ">=", 1, [], "none"),
                object_filtering.Rule("y", ">=", 1, [], "none"),
            ]),
            _else=True
        )
        result = object_filtering.explain_expression(cond)
        assert "If the following condition holds:" in result
        assert "the object is a Shape." in result
        assert "All of the following conditions must be met:" in result
        assert "x is greater than or equal to 1." in result
        assert "y is greater than or equal to 1." in result
        assert "This condition is always true." in result

class TestExplainFilter(unittest.TestCase):
    def test_simple_rule_filter(self):
        f = object_filtering.ObjectFilter(
            name="Area Check",
            description="Checks minimum area.",
            priority=0,
            object_types=["Shape"],
            logical_expression=object_filtering.Rule("area", ">=", 4, [], "none")
        )
        result = object_filtering.explain_filter(f)
        expected = (
            "Filter \"Area Check\": Checks minimum area.\n"
            "This filter applies to objects of type: Shape.\n"
            "area is greater than or equal to 4."
        )
        assert result == expected

    def test_bool_filter(self):
        f = object_filtering.ObjectFilter(
            name="Pass All",
            description="Always passes.",
            priority=0,
            object_types=["object"],
            logical_expression=True
        )
        result = object_filtering.explain_filter(f)
        expected = (
            "Filter \"Pass All\": Always passes.\n"
            "This filter applies to objects of type: object.\n"
            "This condition is always true."
        )
        assert result == expected

    def test_multiple_object_types(self):
        f = object_filtering.ObjectFilter(
            name="Multi Type",
            description="Accepts multiple types.",
            priority=0,
            object_types=["Shape", "Point"],
            logical_expression=True
        )
        result = object_filtering.explain_filter(f)
        assert "This filter applies to objects of types: Shape, and Point." in result

    def test_three_object_types(self):
        f = object_filtering.ObjectFilter(
            name="Tri Type",
            description="Three types.",
            priority=0,
            object_types=["Shape", "Point", "Line"],
            logical_expression=True
        )
        result = object_filtering.explain_filter(f)
        assert "This filter applies to objects of types: Shape, Point, and Line." in result

    def test_conditional_filter(self):
        f = object_filtering.ObjectFilter(
            name="Conditional Check",
            description="Conditionally checks area.",
            priority=0,
            object_types=["Shape", "Point"],
            logical_expression=object_filtering.ConditionalExpression(
                _if=object_filtering.Rule("$CLASS$", "==", "Shape", [], "none"),
                _then=object_filtering.Rule("area", ">=", 4, [], "none"),
                _else=True
            )
        )
        result = object_filtering.explain_filter(f)
        assert "Filter \"Conditional Check\": Conditionally checks area." in result
        assert "If the following condition holds:" in result
        assert "the object is a Shape." in result
        assert "area is greater than or equal to 4." in result
        assert "This condition is always true." in result

class TestExplainExpressionInvalid(unittest.TestCase):
    def test_invalid_type(self):
        with pytest.raises(TypeError):
            object_filtering.explain_expression(42)

    def test_plain_dict(self):
        with pytest.raises(TypeError):
            object_filtering.explain_expression({"criterion": "x"})
