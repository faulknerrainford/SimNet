from Agent import Agent
from random import random


class FallAgent(Agent):

    def __init__(self, agent_id):
        super(FallAgent, self).__init__(agent_id)
        self.mobility = None
        self.energy = None
        self.confidence = None
        self.mobility_resources = None
        self.confidence_resources = None
        self.cenergy = None

    def perception(self, tx, intf):
        super(FallAgent, self).perception(tx, intf)
        edges = self.view[1:]
        # filter out options requiring too much energy
        valid_edges = []
        self.mobility = intf.getnodevalue(tx, self.id, "mobility", "Agent")
        if random() > self.mobility:
            # find hospital in edges
            for edge in edges:
                if edge.end_node["name"] == "Hos":
                    # perception only returns edge to hospital as only valid edge
                    valid_edges = valid_edges + edge
        else:
            self.energy = intf.getnodevalue(tx, self.id, "energy", "Agent")
            for edge in edges:
                if self.energy > [-edge["energy"] - edge.end_node["energy"]]:
                    valid_edges = valid_edges + edge
        self.view[1:] = valid_edges

    def choose(self, tx, intf):
        super(FallAgent, self).choose(tx, intf)
        # filter out options where the agent does not reach the effort threshold
        options = []
        self.confidence = intf.getnodevalue(tx, self.id, "confidence", "Agent")
        self.mobility_resources = intf.getnodevalue(tx, self.id, "mob_res", "Agent")
        self.confidence_resources = intf.getnodevalue(tx, self.id, "conf_res", "Agent")
        for edge in self.view[1:]:
            if edge["effort"] <= edge["mob"] * (self.mobility + self.confidence * self.mobility_resources) + \
                    edge["conf"] * (self.confidence + self.mobility * self.confidence_resources):
                options = options + edge
        # choose based on current highest worth edge
        # ignores edges with no worth score, these are not choosable edges, they are primarily edges indicating a fall
        choice = {"worth": -0.1}
        for edge in options:
            if "worth" in edge.keys():
                if edge["worth"] > choice["worth"]:
                    choice = edge
        return choice

    def learn(self, tx, intf, choice):
        super(FallAgent, self).learn(tx, intf, choice)
        # modify mob, conf, res and energy based on new node
        if "modm" in choice.end_node.keys():
            intf.updateagent(tx, self.id, "mobility", choice.end_node["modm"]+self.mobility)
        if "modc" in choice.end_node.key():
            intf.updateagent(tx, self.id, "confidence", choice.end_node["modc"]+self.confidence)
        if "modrc" in choice.end_node.key():
            intf.updateagent(tx, self.id, "conf_res", choice.end_node["modrc"]+self.confidence_resources)
        if "modrm" in choice.end_node.keys():
            intf.updateagent(tx, self.id, "mob_res", choice.end_node["modrm"]+self.mobility)
        if "energy" in choice.end_node.keys():
            intf.updateagent(tx, self.id, "energy", choice.end_node["energy"]+self.cenergy)
            self.cenergy = choice.end_node["energy"]+self.cenergy
        # update incoming edge worth
        worth = 0
        if self.energy < self.cenergy:
            worth = worth - 1
        elif self.energy > self.cenergy:
            worth = worth + 1
        intf.updateedge(tx, choice, "worth", choice["worth"]+worth, uid="name")

    def payment(self, tx, intf):
        super(FallAgent, self).payment(tx, intf)
        # TODO: deduct energy used in move
        # TODO: mod variables based on edges

    def move(self, tx, intf):
        super(FallAgent, self).move(tx, intf)
