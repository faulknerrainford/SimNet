from Agent import Agent


class FallAgent(Agent):

    def __init__(self, agent_id, params):
        super(FallAgent, self).__init__(agent_id, params)
        # set up properties of an agent.
        [self.mobility, self.confidence, self.mobility_resources, self.confidence_resources, self.energy] = params

    def perception(self, tx, intf):
        super(FallAgent, self).perception(tx, intf)
        edges = self.view[1:]
        # filter out options requiring too much energy
        valid_edges = []
        # TODO: Check for fall, if fall then perception only returns edge to hospital
        self.energy = intf.getnodevalue(tx, self.id, "energy", "Agent")
        for edge in edges:
            if self.energy > [-edge["energy"] - edge.end_node["energy"]]:
                valid_edges = valid_edges + edge
        self.view[1:] = valid_edges

    def choose(self, tx, intf):
        super(FallAgent, self).choose(tx, intf)
        # filter out options where the agent does not reach the effort threshold
        options = []
        for edge in self.view[1:]:
            if edge["effort"] <= edge["mob"] * (self.mobility + self.confidence * self.mobility_resources) + \
                    edge["conf"] * (self.confidence + self.mobility * self.confidence_resources):
                options = options + edge
        # choose based on current highest worth edge
        choice = options[0]
        for edge in options:
            if edge["worth"] > choice["worth"]:
                choice = edge
        return choice

    def learn(self, tx, intf, choice):
        super(FallAgent, self).learn(tx, intf, choice)
        # TODO: modify mob and conf based on node and/or edge used
        # TODO: update incoming edge worth

    def payment(self, tx, intf):
        super(FallAgent, self).payment(tx, intf)
        # TODO: deduct energy used

    def move(self, tx, intf):
        super(FallAgent, self).move(tx, intf)
