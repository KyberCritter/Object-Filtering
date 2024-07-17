# Filter Specifications

(c) 2024 Scott Ratchford

This file is licensed under the MIT License. See LICENSE.txt for details.

Filters are JSON objects containing conditional checks and comparisons to perform on the instance variables, properties, and methods of any Python object. To use a method in a filter, the method definition must be decorated with the `@filter_criterion'. Instance variables and properties can be used without the decorator.

## Extended Backus-Naur Form of Filter Specifications

This format defines the representation of a filter in JSON. When parsing filters, whitespace between components is ignored.

```EBNF
# filter, the highest level. Always defines at least 1 logical_component.
filter ::= "{\"name\":" string ", \"description\":" string ",\"priority\":" nonnegative_integer ",\"object_types\": [" object_types "], \"logical_component\":" logical_component "}"

# Non-logic information for filter
object_types ::= string | string "," object_types

# logical_components, the second level. All logical_components are interchangeable in any circumstance.
logical_components ::= logical_component | logical_component logical_components
logical_component ::= filter | rule | conditional_statement | group_expression
rule ::= "\"criterion:\"" string ", \"operator\":" operator ", \"comparison_value:\"" comparison_value ", \"parameters:\"" parameter_list ", \"multi_object_behavior:\"" multi_object_behavior
conditional_statement ::= "{\"if\":" logical_components ", \"then\":" logical_components ", \"else\":" logical_components "}"
group_expression ::= "{ \"condition\":" condition ", \"logical_components\":" logical_components "}"

# Portions of logical_components. Cannot be used on their own.
operator ::= "\"<\"" | "\"<=\"" | "\"==\"" | "\"!=\"" | "\">=\"" | "\">\""
comparison_value ::= integer | float | string | boolean
condition ::= "and" | "or"
parameter_list ::= "[]" | "[" parameters "]"
parameters ::= comparison_value | comparison_value "," parameters
multi_object_behavior ::= "\"none\"" | "\"add\"" | "\"each_meets_criterion\"" | "\"each_equal_in_object\""

# Basic data types. Equivalent to their JSON EBNF. (nonnegative_integer is not a data type in JSON.)
integer ::= "-" digits | nonnegative_integer
digits ::= digit | digit digits
digit ::= "0" | nonzero_digit
nonzero_digit ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
nonnegative_integer ::= "0" | nonzero_digit digits | digits

float ::= integer "." nonnegative_integer | integer "." nonnegative_integer exponent | integer exponent
exponent ::= exponent_letter "+" nonnegative_integer | exponent_letter integer
exponent_letter ::= "e" | "E"

string ::=  "\"\"" | "\"" chars "\""
chars ::= char | char chars
char ::= " " | "!" | "\"" | "#" | "$" | "%" | "&" | "'" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | ":" | ";" | "<" | "=" | ">" | "?" | "@" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "[" | "\\" | "]" | "^" | "_" | "`" | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "{" | "|" | "}" | "~"

boolean ::= "true" | "false"
```

## Terms

- **Logical Expression**: A single boolean value, rule, group expression, conditional expression, or filter.
- **Boolean Value**: The literal value True or False.
- **Rule**: The lowest-level logical expression, which cannot contain any other logical expressions. Evaluates to True or False based on the criterion within.
- **Group Expression**: A group of logical expressions, joined with a logical operator.
- **Conditional Expression**: Logical expressions that evaluate based on the criteria of the other logical expressions within.
- **Operator**: Comparison symbols. <, <=, ==, !=, >=, >.
- **Logical Operator**: Terms that define how many logical expressions within must evaluate to True for the whole group to be True. "and" or "or".

## Detailed Filter Structure

### Filter

A filter is an object that includes several key elements:

- **name**: The name of the filter.
- **description**: A brief explanation of what the filter does.
- **priority**: A number indicating how important the filter is (lower numbers indicate higher priority, must be >= 0).
- **object_types**: A list of types of objects the filter applies to.
- **logical_expression**: A single logical expression, as defined above.

### Rule

A rule specifies a single condition to check and includes:

- **Criterion**: The property to check (e.g., width, height).
- **Operator**: The operator used to compare the criterion with the comparison value. Defined above.
- **Comparison Value**: The value to compare the property against.
- **Parameters**: Additional values to use in the comparison, if the criterion is a method.
- **Multi Value Behavior**: How a list of values returned by evaluating the criterion should be evaluated. For advanced usage only. "none", "add", "each_meets_criterion", or "each_equal_in_object".

### Operators

Operators define how to compare values:

| Operator | Meaning           |
|----------|-------------------|
| <        | Less than         |
| <=       | Less than or equal|
| ==       | Equal to          |
| !=       | Not equal to      |
| >=       | Greater than or equal |
| >        | Greater than      |

### Group Expressions

Group expressions define the conditions and rules that the filter uses. They use a logical operator (defined above) to determine how many of the logical expressions must evaluate to **True** for the whole group expression to evaluate to **True**.

- **logical_operator**: The logical operator to use. "and" indicates that all logical expressions evaluate to **True** for the group expression to be **True**. "or" indicates that 1 or more logical expressions must evaluate to **True** for the group expression to be **True**.
- **logical_expressions**: One or more logical expressions of any kind. Surrounded by `[ ]`.

### Conditional Expression

A conditional expression includes three parts:

- **if**: The first logical expression to evaluate. If the logical expression evaluates to **True**, the *then* conditional expression will be evaluated. If the *if* portion evaluates to **False**, the *else* portion will be evaluated.
- **then**: A logical expression, only evaluated if *if* is **True**. If *if* is **True** and *then* is **True**, then the conditional expression is **True**. If *if* is **True** and *then* is **False**, then the conditional expression is **False**.
- **else**: A logical expression, only evaluated if *if* is **False**. If *if* is **False** and *else* is **True**, then the conditional expression is **True**. If *if* is **False** and *else* is **False**, then the conditional expression is **False**.

To evaluate to **True**, either the *if* and *then* conditions must evaluate to **True**, or the *if* conditions must evaluate to **False** and the *else* conditions must evaluate to **True**.

```JSON
{
    "name": "Fits in Box",
    "description": "A sample filter demonstrating potential conditions for an animal to fit in a cardboard box.",
    "priority": 2,
    "object_types": ["Animal"],
    "logical_expression": [
        {
            "logical_operator": "or",
            "logical_expressions": [
                {
                    "if": {
                        "logical_operator": "and",
                        "logical_expressions": [
                            {"criterion": "species", "operator": "==", "comparison_value": "cat", "parameters": [], "multi_value_behavior": "none"},
                            {"criterion": "weight", "operator": "<", "comparison_value": 8.9, "parameters": [], "multi_value_behavior": "none"},
                        ]
                    },
                    "then": {
                        "logical_operator": "or",
                        "logical_expressions": [
                            {"criterion": "height", "operator": "<=", "comparison_value": 1.5, "parameters": [], "multi_value_behavior": "none"},
                            {"criterion": "length", "operator": "<=", "comparison_value": 2, "parameters": [], "multi_value_behavior": "none"}
                        ]
                    },
                    "else": {
                        "logical_operator": "and",
                        "logical_expressions": [
                            {"criterion": "species", "operator": "==", "comparison_value": "cat", "parameters": [], "multi_value_behavior": "none"}
                        ]
                    }
                },
                {
                    "if": {
                        "condition": "and",
                        "rules": [
                            {"criterion": "species", "operator": "==", "comparison_value": "dog", "parameters": [], "multi_value_behavior": "none"},
                            {"criterion": "weight", "operator": "<", "comparison_value": 8.9, "parameters": [], "multi_value_behavior": "none"},
                        ]
                    },
                    "then": {
                        "condition": "or",
                        "rules": [
                            {"criterion": "height", "operator": "<=", "comparison_value": 1.5, "parameters": [], "multi_value_behavior": "none"},
                            {"criterion": "length", "operator": "<=", "comparison_value": 2.5, "parameters": [], "multi_value_behavior": "none"}
                        ]
                    },
                    "else": false,
                }
            ]
        },
        {
            "logical_operator": "and",
            "logical_expressions": [
                {"criterion": "width", "operator": "<=", "comparison_value": 20, "parameters": [], "multi_value_behavior": "none"},
                {"criterion": "rounded_length", "operator": "<=", "comparison_value": 62, "parameters": [], "multi_value_behavior": "none"}
            ]
        }
    ]
}
```
