import random

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.Value import Value
from mesa import Model
from mesa.time import RandomActivation


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent."""

    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name)
        self.preference = preferences

    def step(self):
        super().step()

    def get_preference(self):
        return self.preference

    def generate_preferences(self, list_items):
        # shuffle the criterions to get the order of preferences
        list_criterions = [criterion_name for criterion_name in CriterionName]
        random.shuffle(list_criterions)
        self.preference.set_criterion_name_list(list_criterions)

        # for each criterion draw a random set of preferences and evaluate all the items according to it
        for criterion_name in CriterionName : 
            criterion_range = criterion_name.criterion_range
            criterion_span = criterion_range[1] - criterion_range[0]
            p1 = (random.random() / 3 ) * criterion_span + criterion_range[0]
            p2 = (random.random() / 3 + 1 / 3 ) * criterion_span + criterion_range[0]
            p3 = (random.random() / 3 + 2 / 3 ) * criterion_span + criterion_range[0]
            for item in list_items :
                numerical_value = item.get_criterion_value(criterion_name)
                if numerical_value < p1 : 
                    criterion_value = CriterionValue(item, criterion_name, Value.VERY_BAD)
                elif numerical_value >= p1 and numerical_value < p2 : 
                    criterion_value = CriterionValue(item, criterion_name, Value.BAD)
                elif numerical_value >= p2 and numerical_value < p3 : 
                    criterion_value = CriterionValue(item, criterion_name, Value.GOOD)
                elif numerical_value >= p3 : 
                    criterion_value = CriterionValue(item, criterion_name, Value.VERY_GOOD)
                self.preference.add_criterion_value(criterion_value)


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self, list_items):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        A1 = ArgumentAgent(1, self, "A1", Preferences())
        A2 = ArgumentAgent(2, self, "A2", Preferences())
        A1.generate_preferences(list_items)
        A2.generate_preferences(list_items)
        self.schedule.add(A1)
        self.schedule.add(A2)

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()


if __name__ == "__main__":

    list_items = [
        Item("Diesel Engine", "A super cool diesel engine",
            {
                CriterionName.PRODUCTION_COST:12330,
                CriterionName.CONSUMPTION:6.3,
                CriterionName.DURABILITY:3.8,
                CriterionName.ENVIRONMENT_IMPACT:4.8,
                CriterionName.NOISE:65,
            }
            ),
        Item("Electric Engine", "A very quiet engine", 
            {
                CriterionName.PRODUCTION_COST:17100,
                CriterionName.CONSUMPTION:0,
                CriterionName.DURABILITY:3,
                CriterionName.ENVIRONMENT_IMPACT:2.2,
                CriterionName.NOISE:48,
            }
            )
    ]

    argument_model = ArgumentModel(list_items)
    print(argument_model.schedule.agents[0].preference)
    print(argument_model.schedule.agents[1].preference)
    # To be completed
