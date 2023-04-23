from communication.preferences.CriterionName import CriterionName
from communication.preferences.Value import Value


class CoupleValue:
    def __init__(self, criterion_name: CriterionName, value: Value):
        self.criterion_name = criterion_name
        self.value = value

    def __repr__(self) -> str:
        return f"{self.criterion_name} = {self.value}"

    def __eq__(self, other) -> bool:
        return self.criterion_name == other.criterion_name and self.value == other.value
