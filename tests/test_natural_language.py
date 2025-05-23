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
        # square = Shape(3, 4)
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

if __name__ == '__main__':
    pytest.main()
