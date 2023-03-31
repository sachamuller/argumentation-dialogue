import random

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
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

    def __init__(
        self, unique_id, model, name, preferences: Preferences, initiate_proposal=False
    ):
        super().__init__(unique_id, model, name)
        self.preferences = preferences
        self.items = [
            criterion.get_item()
            for criterion in self.preferences.get_criterion_value_list()
        ]
        self.initiate_proposal = initiate_proposal

    def accept(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ACCEPT,
            item,
        )

    def propose(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.PROPOSE,
            item,
        )

    def ask_why(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ASK_WHY,
            item,
        )

    def commit(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.COMMIT,
            item,
        )
        self.items.remove(item)

    def argue(self, argument, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ARGUE,
            argument,
        )

    def step(self):
        super().step()
        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.PROPOSE:
                if self.preferences.is_item_among_top_10_percent(
                    message.get_content(), self.items
                ):
                    self.accept(message.get_content(), message.get_exp())
                else:
                    self.ask_why(message.get_content(), message.get_exp())
            elif message.get_performative() in (
                MessagePerformative.ACCEPT,
                MessagePerformative.COMMIT,
            ):
                if message.get_content() in self.items:
                    self.commit(message.get_content(), message.get_exp())
            elif message.get_performative() == MessagePerformative.ASK_WHY:
                self.argue(None, message.get_exp())

        # TODO: should be able to manage multiple proposals in parallel at a time
        if (
            len(messages) == 0
            and self.initiate_proposal  # Agent qui peut faire des propositions
            and self.model.schedule.get_agent_count() > 0  # Au moins 2 agents
            and len(self.items) > 0  # Au moins 1 item disponible
        ):
            other_agent = random.choice(
                [agent for agent in self.model.schedule.agent_buffer() if agent != self]
            )
            self.propose(random.choice(self.items), other_agent.unique_id)

    def generate_preferences(self, list_items: list[Item]):
        self.items = list_items.copy()
        # shuffle the criterions to get the order of preferences
        list_criterions = [criterion_name for criterion_name in CriterionName]
        random.shuffle(list_criterions)
        self.preferences.set_criterion_name_list(list_criterions)

        # for each criterion draw a random set of preferences and evaluate all the items according to it
        for criterion_name in CriterionName:
            criterion_range = criterion_name.criterion_range
            criterion_span = criterion_range[1] - criterion_range[0]
            p1 = (random.random() / 3) * criterion_span + criterion_range[0]
            p2 = (random.random() / 3 + 1 / 3) * criterion_span + criterion_range[0]
            p3 = (random.random() / 3 + 2 / 3) * criterion_span + criterion_range[0]
            for item in list_items:
                numerical_value = item.get_criterion_value(criterion_name)
                if numerical_value < p1:
                    criterion_value = CriterionValue(
                        item, criterion_name, Value.VERY_BAD
                    )
                elif numerical_value >= p1 and numerical_value < p2:
                    criterion_value = CriterionValue(item, criterion_name, Value.BAD)
                elif numerical_value >= p2 and numerical_value < p3:
                    criterion_value = CriterionValue(item, criterion_name, Value.GOOD)
                elif numerical_value >= p3:
                    criterion_value = CriterionValue(
                        item, criterion_name, Value.VERY_GOOD
                    )
                self.preferences.add_criterion_value(criterion_value)

    def send_message(self, message):
        super().send_message(message)
        print(message)


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self, list_items):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        A1 = ArgumentAgent(1, self, "A1", Preferences(), True)
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
        Item(
            "Diesel Engine",
            "A super cool diesel engine",
            {
                CriterionName.PRODUCTION_COST: 12330,
                CriterionName.CONSUMPTION: 6.3,
                CriterionName.DURABILITY: 3.8,
                CriterionName.ENVIRONMENT_IMPACT: 4.8,
                CriterionName.NOISE: 65,
            },
        ),
        Item(
            "Electric Engine",
            "A very quiet engine",
            {
                CriterionName.PRODUCTION_COST: 17100,
                CriterionName.CONSUMPTION: 0,
                CriterionName.DURABILITY: 3,
                CriterionName.ENVIRONMENT_IMPACT: 2.2,
                CriterionName.NOISE: 48,
            },
        ),
    ]

    argument_model = ArgumentModel(list_items)
    print(argument_model.schedule.agents[0].preferences)
    print(argument_model.schedule.agents[1].preferences)
    for _ in range(15):
        argument_model.step()
