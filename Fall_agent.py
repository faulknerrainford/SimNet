from Agent import Agent
from random import random
from numpy.random import normal
from numpy import exp


class FallAgent(Agent):

    def __init__(self, agent_id):
        super(FallAgent, self).__init__(agent_id, nuid="name")
        self.mobility = None
        self.energy = None
        self.confidence = None
        self.mobility_resources = None
        self.confidence_resources = None
        self.current_energy = None

    def generator(self, tx, intf, params):
        # generate a random set of parameters based on a distribution with mean set by params
        [mobility, confidence, energy] = params
        self.mobility = normal(mobility, 0.05)  # draw from normal distribution centred on given value
        self.energy = normal(energy, 0.05)
        self.confidence = normal(confidence, 0.05)
        # Add agent with params to ind in graph with resources starting at 0
        intf.addagent(tx, {"name": "Ind"}, "Agent", {"mob": self.mobility, "conf": self.confidence, "mob_res": 0,
                                                     "conf_res": 0, "energy": self.energy}, "name")

    @staticmethod
    def positive(num):
        if num < 0:
            return 0
        else:
            return num

    def perception(self, tx, intf):
        super(FallAgent, self).perception(tx, intf)
        edges = self.view[1:]
        # filter out options requiring too much energy
        valid_edges = []
        self.mobility = intf.getnodevalue(tx, self.id, "mob", "Agent")
        self.energy = intf.getnodevalue(tx, self.id, "energy", "Agent")
        self.current_energy = self.energy
        if self.view:
            destinations = [edge.end_node["name"] for edge in edges]
            if self.mobility <= 0:
                if "Care" in destinations and self.mobility <= 0:
                    # select care edge as only choice
                    valid_edges = [edges[destinations.index("Care")]]
            elif 1 < self.mobility and "Ind" in destinations:
                # select "Ind" edge as only choice
                valid_edges = [edges[destinations.index("Ind")]]
            elif random() < exp(-3*self.mobility) and self.view[0]["name"] != "Hos":
                valid_edges = [edges[destinations.index("Hos")]]
            elif self.view[0]["name"] == "Hos":
                if self.mobility > self.view[0]["discharged"]:
                    valid_edges = [edges[destinations.index("Home")]]
            else:
                for edge in edges:
                    if not edge.end_node["name"] in ["Care", "Ind", "Hos"]:
                        cost = 0
                        if edge["energy"]:
                            cost = cost + edge["energy"]
                        if edge.end_node["energy"]:
                            cost = cost + edge.end_node["energy"]
                        if self.energy > -cost:
                            valid_edges = valid_edges + [edge]
        self.view[1:] = valid_edges

    def choose(self, tx, intf):
        super(FallAgent, self).choose(tx, intf)
        # filter out options where the agent does not reach the effort threshold
        options = []
        self.confidence = intf.getnodevalue(tx, self.id, "conf", "Agent")
        self.mobility_resources = intf.getnodevalue(tx, self.id, "mob_res", "Agent")
        self.confidence_resources = intf.getnodevalue(tx, self.id, "conf_res", "Agent")
        if len(self.view[1:]) < 2:
            if self.view[1:]:
                choice = self.view[1:][0]
            else:
                choice = self.view[1:]
        else:
            for edge in self.view[1:]:
                if edge["effort"] <= edge["mobility"] * (self.mobility + self.confidence * self.mobility_resources) + \
                        edge["confidence"] * (self.confidence + self.mobility * self.confidence_resources):
                    options = options + [edge]
            # choose based on current highest worth edge ignores edges with no worth score, these are not choosable
            # edges, they are primarily edges indicating a fall
            if not options:
                return None
            choice = options[0]
            for edge in options:
                if "worth" in edge and "worth" in choice:
                    if edge["worth"] > choice["worth"]:
                        choice = edge
                elif "worth" in edge:
                    choice = edge
        return choice

    def learn(self, tx, intf, choice):
        super(FallAgent, self).learn(tx, intf, choice)
        # modify mob, conf, res and energy based on new node
        if "modm" in choice.end_node:
            intf.updateagent(tx, self.id, "mob", self.positive(normal(choice.end_node["modm"], 0.05) + self.mobility))
        if "modc" in choice.end_node:
            intf.updateagent(tx, self.id, "conf", self.positive(normal(choice.end_node["modc"], 0.05) +
                                                                self.confidence))
        if "modrc" in choice.end_node:
            intf.updateagent(tx, self.id, "conf_res",
                             self.positive(normal(choice.end_node["modrc"], 0.05) + self.confidence_resources))
        if "modrm" in choice.end_node:
            intf.updateagent(tx, self.id, "mob_res", self.positive(normal(choice.end_node["modrm"], 0.05) +
                                                                   self.mobility))
        if "energy" in choice.end_node:
            self.current_energy = normal(choice.end_node["energy"], 0.05) + self.current_energy
            intf.updateagent(tx, self.id, "energy", self.current_energy)
        if choice.end_node["name"] == "Care":
            clock = tx.run("MATCH (a:Clock) "
                           "RETURN a.time").values()[0][0]
            intf.updateagent(tx, self.id, "time", clock)
        # # update incoming edge worth
        # if "worth" in choice:
        #     worth = 0
        #     if self.energy < self.current_energy:
        #         worth = worth - 1
        #     elif self.energy > self.current_energy:
        #         worth = worth + 1
        #     intf.updateedge(tx, choice, "worth", choice["worth"] + worth, uid="name")

    def payment(self, tx, intf):
        super(FallAgent, self).payment(tx, intf)
        # Deduct energy used on edge
        if "energy" in self.choice.keys():
            self.current_energy = normal(self.choice["energy"], 0.05) + self.current_energy
            intf.updateagent(tx, self.id, "energy", self.current_energy)
        # mod variables based on edges
        if "modm" in self.choice:
            intf.updateagent(tx, self.id, "mob", self.positive(normal(self.choice["modm"], 0.05) + self.mobility))
        if "modc" in self.choice:
            intf.updateagent(tx, self.id, "conf", self.positive(normal(self.choice["modc"], 0.05) + self.confidence))

    def move(self, tx, intf):
        super(FallAgent, self).move(tx, intf)
        if intf.getnodevalue(tx, self.id, "discharged", "Agent"):
            intf.updateagent(tx, self.id, "discharged", 0)
