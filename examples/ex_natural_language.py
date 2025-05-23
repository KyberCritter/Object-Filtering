# (c) 2025 Scott Ratchford
# Example usage of the natural-language filter explainer

#!/usr/bin/env python3
from object_filtering.object_filtering import ObjectFilter, Rule, GroupExpression
from object_filtering.natural_language import explain_filter


large_filter = ObjectFilter(
    name="Shape Area",
    description="Determines whether Shape is large.",
    priority=0,
    object_types=["Shape",],
    logical_expression=GroupExpression(
        logical_operator="and",
        logical_expressions=[
            Rule(
                criterion="area",
                operator=">=",
                comparison_value=4,
                parameters=[],
                multi_value_behavior="none"
            ),
            Rule(
                criterion="volume",
                operator=">=",
                comparison_value=8,
                parameters=[2,],
                multi_value_behavior="none"
            ),
            GroupExpression(
                logical_operator="or",
                logical_expressions=[
                    Rule(
                        criterion="area_if_stretched",
                        operator=">=",
                        comparison_value=9,
                        parameters=[2, 3],
                        multi_value_behavior="none"
                    ),
                    Rule(
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

if __name__ == "__main__":
    # Run the explainer and print the result
    description = explain_filter(large_filter)
    print(description)
