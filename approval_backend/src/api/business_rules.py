"""
PUBLIC_INTERFACE

This module integrates the python-business-rules library with the approval workflow system,
allowing JSON-based business rules to be evaluated to drive conditional logic in workflow steps/blocks.
"""
from business_rules.engine import run_all

# PUBLIC_INTERFACE
def evaluate_business_rule(rules: dict, variables_data: dict, actions: object) -> bool:
    """
    Evaluate business rules as JSON using business_rules library.

    Args:
        rules: JSON object of rule(s)
        variables_data: contextual variables for the rule engine
        actions: actions module/class to execute

    Returns:
        bool: True if rules allow action/progression, False otherwise.
    """
    result = run_all(rule_list=rules, defined_variables=variables_data, defined_actions=actions)
    return result
