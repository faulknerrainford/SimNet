from Agent import Agent


class ToyAgent(Agent):

    def __init__(self, agentid):
        super(ToyAgent, self).__init__(agentid)

    def choose(self, tx, intf):
        super(ToyAgent, self).choose(tx, intf)
        # node = self.view[0]
        edges = self.view[1:]
        mincost = 60
        choice = None
        for edge in edges:
            if edge["cost"] < mincost:
                mincost = edge["cost"]
                choice = edge
        return choice

    def learn(self, tx, intf, choice):
        super(ToyAgent, self).learn(tx, intf, choice)
