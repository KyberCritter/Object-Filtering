# (c) 2025 Scott Ratchford
# Example usage of the natural-language filter explainer

#!/usr/bin/env python3
from object_filtering.object_filtering import ObjectFilter, Rule, GroupExpression
from object_filtering.natural_language import explain_filter

# Construct a sample ObjectFilter
sample_filter = ObjectFilter(
    name="AdultHeightFilter",
    description="Selects adults of acceptable height",
    priority=1,
    object_types=["Person"],
    logical_expression=GroupExpression(
        logical_operator="and",
        logical_expressions=[
            # Age at least 18
            Rule(
                criterion = "age",
                operator = ">=",
                comparison_value = 18,
                parameters = [],
                multi_value_behavior = "none"
            ),
            # Height less than 200 cm
            Rule(
                criterion = "height_cm",
                operator = "<",
                comparison_value = 200,
                parameters = [],
                multi_value_behavior = "none"
            ),
            GroupExpression(
                logical_operator="or",
                logical_expressions=[
                    # Height greater than 150 cm
                    Rule(
                        criterion = "height_cm",
                        operator = ">",
                        comparison_value = 150,
                        parameters = [],
                        multi_value_behavior = "none"
                    ),
                    # Height equal to 100 cm
                    Rule(
                        criterion = "height_cm",
                        operator = "==",
                        comparison_value = 100,
                        parameters = [],
                        multi_value_behavior = "none"
                    ),
                    # Height equal to 102 cm
                    Rule(
                        criterion = "height_cm",
                        operator = "==",
                        comparison_value = 102,
                        parameters = [],
                        multi_value_behavior = "none"
                    ),
                ]
            )
        ]
    )
)

if __name__ == "__main__":
    # Run the explainer and print the result
    description = explain_filter(sample_filter)
    print(description)
