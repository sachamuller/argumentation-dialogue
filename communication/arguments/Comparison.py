from communication.preferences.CriterionName import CriterionName


class Comparison:
    """
    Comparison class.
    This class implements a comparison object used in argument object.

    attr:
        best_criterion_name
        worst_criterion_name
    """

    def __init__(
        self, best_criterion_name: CriterionName, worst_criterion_name: CriterionName
    ):
        self.best_criterion_name = best_criterion_name
        self.worst_criterion_name = worst_criterion_name
