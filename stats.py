from pw_argumentation import ArgumentModel, ArgumentAgent
from communication.preferences.Item import Item
from communication.preferences.CriterionName import CriterionName
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

list_items = [
    Item(
        "A",
        "A super cool diesel engine",
        {
            CriterionName.PRODUCTION_COST: 12330,
            CriterionName.CONSUMPTION: 6.3,
            CriterionName.DURABILITY: 3.8,
            CriterionName.ENVIRONMENT_IMPACT: 4.8,
            CriterionName.NOISE: 60,
        },
    ),
    Item(
        "B",
        "A very quiet engine",
        {
            CriterionName.PRODUCTION_COST: 17100,
            CriterionName.CONSUMPTION: 0,
            CriterionName.DURABILITY: 3,
            CriterionName.ENVIRONMENT_IMPACT: 2.2,
            CriterionName.NOISE: 40,
        },
    ),
    Item(
        "C",
        "So fast you can't even see it",
        {
            CriterionName.PRODUCTION_COST: 19784,
            CriterionName.CONSUMPTION: 8,
            CriterionName.DURABILITY: 2.5,
            CriterionName.ENVIRONMENT_IMPACT: 3,
            CriterionName.NOISE: 75,
        },
    ),
    Item(
        "D",
        "Lifts your whole family like a charm",
        {
            CriterionName.PRODUCTION_COST: 15000,
            CriterionName.CONSUMPTION: 9.2,
            CriterionName.DURABILITY: 3.7,
            CriterionName.ENVIRONMENT_IMPACT: 3.7,
            CriterionName.NOISE: 80,
        },
    ),
]


def compute_percentage_of_agreements_and_ranks(number_runs, list_items=list_items):
    # both counters must contain same values as agents should commit on same thing
    agreed_on = [Counter(), Counter()]
    commited_item_rank = [Counter(), Counter()]

    for n in range(number_runs):
        argument_model = ArgumentModel(list_items)

        print(f"\nExperiment {n} :")
        print(argument_model.schedule.agents[0].preferences)
        print(argument_model.schedule.agents[1].preferences)
        for _ in range(100):
            argument_model.step()
        agents: list[ArgumentAgent] = argument_model.schedule.agents

        favorite_items_sorted = [
            [
                item.get_name()
                for item in agent.preferences.sort_item_list_by_preference(list_items)
            ]
            for agent in agents
        ]

        for i, agent in enumerate(agents):
            commited = False
            for message in agent.get_messages():
                if message.get_performative() == MessagePerformative.COMMIT:
                    commited = True
                    commit_on = message.get_content()
                    if commit_on is None:
                        agreed_on[i]["None"] += 1
                    elif isinstance(commit_on, Item):
                        agreed_on[i][commit_on.get_name()] += 1
                        commited_item_rank[i][
                            favorite_items_sorted[i].index(commit_on.get_name()) + 1
                        ] += 1

                    else:
                        raise ValueError("Commit can only contain object or None")
            if not commited:
                agreed_on[i]["No commit"] += 1
        MessageService.reset()
    return agreed_on, commited_item_rank


def compute_confusion_matrix_of_ranks(number_runs, list_items=list_items):
    confusion_matrix = np.zeros((len(list_items), len(list_items)))

    for n in range(number_runs):
        MessageService.reset()
        argument_model = ArgumentModel(list_items)
        print(f"\nExperiment {n} :")
        for _ in range(100):
            argument_model.step()
        agents: list[ArgumentAgent] = argument_model.schedule.agents

        favorite_items_sorted = [
            [
                item.get_name()
                for item in agent.preferences.sort_item_list_by_preference(list_items)
            ]
            for agent in agents
        ]
        agents_ranks = [None, None]
        for i, agent in enumerate(agents):
            commited = False
            for message in agent.get_messages():
                if message.get_performative() == MessagePerformative.COMMIT:
                    commited = True
                    commit_on = message.get_content()
                    if commit_on is None:
                        pass
                    elif isinstance(commit_on, Item):
                        rank = favorite_items_sorted[i].index(commit_on.get_name())
                        agents_ranks[i] = rank
                    else:
                        raise ValueError("Commit can only contain object or None")
            if not commited:
                agreed_on[i]["No commit"] += 1
        agent1_rank = agents_ranks[0]
        agent2_rank = agents_ranks[1]
        if agent1_rank is not None and agent2_rank is not None:
            confusion_matrix[agent1_rank, agent2_rank] += 1

    return confusion_matrix


if __name__ == "__main__":
    agreed_on, commited_item_rank = compute_percentage_of_agreements_and_ranks(10000)

    fig, axes = plt.subplots(ncols=len(agreed_on))

    titles = ["Agent 1", "Agent 2"]

    for i in range(len(commited_item_rank)):
        labels, values = zip(*commited_item_rank[i].items())
        labels_values = zip(labels, values)

        indexes = np.arange(len(labels))
        width = 0.8

        axes[i].bar(indexes, values, width)
        axes[i].set_xticks(indexes, labels)
        axes[i].set_title(titles[i])
        axes[i].set_xlabel("Commited on")
        axes[i].set_ylabel("Occurences")
    plt.show()
