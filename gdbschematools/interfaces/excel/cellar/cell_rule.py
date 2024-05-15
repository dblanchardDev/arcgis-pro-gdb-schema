"""
Utility to quickly apply conditional formatting rules to cells consistently.

Author: David Blanchard
"""

from openpyxl.formatting import Rule
from openpyxl.styles import PatternFill, Border, Side
from openpyxl.styles.differential import DifferentialStyle



class CellRule:
    """Create a formula based conditional formatting rule.

    Args:
        formula (str, optional): Formula which when true will flag the cell as an error. Replace the base coordinate in the formula with '<coordinate>' (no quotes) if applicable. Default to None.
        rule_type (str, optional): Type of openpyxl.formatting.Rule to create. Defaults to expression which accepts a formula.
    """ #pylint: disable=line-too-long

    # Style to highlight cells with an error
    ERROR_DIFF_STYLE = DifferentialStyle(
        fill=PatternFill(start_color="E6B8B7", end_color="E6B8B7"),
        border=Border(bottom=Side(color="f2f2f2", style="thin"), top=Side(color="f2f2f2", style="thin")),
    )

    _formula:str = None
    _rule_type:str = None

    def __init__(self, formula:str=None, rule_type:str="expression") -> None:
        self._formula = formula
        self._rule_type = rule_type


    def make_rule_for_cell(self, base_coordinate:str=None) -> Rule:
        """Get a copy of the rule applied to the cell(s) in question.

        Args:
            base_coordinate (str, optional): The coordinate of the the top-left-most cell to which this rule will apply. Defaults to None.

        Returns:
            Rule: The openpyxl formatting rule for the cell(s).
        """ #pylint: disable=line-too-long

        if self._rule_type == "expression":
            if "<coordinate>" in self._formula and base_coordinate is None:
                raise ValueError("Base coordinate must be provided for rules with a coordinate placeholder.")

            updated_formula = self._formula.replace("<coordinate>", base_coordinate)
            return Rule(type="expression", dxf=CellRule.ERROR_DIFF_STYLE, formula=[updated_formula])

        return Rule(type=self._rule_type, dxf=CellRule.ERROR_DIFF_STYLE)


CELL_RULE_NOT_BLANK = CellRule("ISBLANK(<coordinate>)")
CELL_RULE_TEXT_MIN_3 = CellRule("LEN(<coordinate>) < 3")
CELL_RULE_NO_DUPLICATES = CellRule(rule_type="duplicateValues")