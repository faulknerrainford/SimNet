from Agent import Agent
from random import random


class FallAgent(Agent):

    def __init__(self, agent_id, params):
        super(FallAgent, self).__init(agent_id, params)
        # TODO: set up properties of an agent.

    def perception(self):
        super(FallAgent, self).perception()
        # TODO: filter out options requiring too much energy

    def choose(self):
        super(FallAgent, self).choose()
        # TODO: filter out options where the agent does not reach the effort threshold
        # TODO: choose based on current highest worth edge

    def learn(self):
        super(FallAgent, self).learn()
        # TODO: modify mob and conf based on node and/or edge used
        # TODO: update incoming edge worth

    def payment(self):
        super(FallAgent, self).payment()
        # TODO: deduct energy used

    def move(self):
        super(FallAgent, self).move()