from Agent import Agent


class ToyAgent(Agent):

    def __init__(self, agentid, params):
        if len(params) == 1:
            super(ToyAgent, self).__init__(agentid, params)
            self.switch = None
        else:
            raise ValueError("Incorrect parameter length, Toy Agent takes 1 parameter only")

    def choose(self, tx, intf):
        super(ToyAgent, self).choose(tx, intf)
        node = intf.getnode(tx, self.id, "Dancer")
        self.switch = node["switch"]
        edges = self.view[1:]
        if self.switch > 0.5 and edges:
            maxben = 0
            choice = None
            for edge in edges:
                if edge["outlook"] > maxben:
                    maxben = edge["outlook"]
                    choice = edge
        elif edges:
            mincost = 200
            choice = None
            for edge in edges:
                if edge["cost"] < mincost:
                    mincost = edge["cost"]
                    choice = edge
        else:
            choice = None
        return choice

    def learn(self, tx, intf, choice):
        super(ToyAgent, self).learn(tx, intf, choice)
        destination = choice.end_node
        payout = destination["payout"]
        if payout < choice["outlook"]:
            # reset outlook down
            intf.updateedge(tx, choice, "outlook", choice["outlook"]-1)
        elif payout > choice["outlook"]:
            # reset outlook up
            intf.updateedge(tx, choice, "outlook", choice["outlook"]+1)
        prefunds = self.view[0]["funds"]
        postfunds = prefunds + destination["payout"] - choice["cost"]
        if prefunds < postfunds:
            self.switch = self.switch-0.5*self.switch
        else:
            self.switch = self.switch+0.5*self.switch
        if self.switch > 1:
            self.switch = 1
        elif self.switch < 0:
            self.switch = 0
        intf.updatenode(tx, self.view[0], "switch", self.switch)

    def move(self, tx, intf):
        super(ToyAgent, self).move(tx, intf)
        if self.choice:
            node = tx.run("MATCH (n:Dancer) "
                          "WHERE n.id = {id} "
                          "RETURN n", id=self.id).values()[0][0]
            cost = self.choice["cost"]
            payout = self.choice.end_node["payout"]
            intf.updatenode(tx, node, "funds", node["funds"] - cost)
            intf.updatenode(tx, self.choice.start_node, "funds", self.choice.start_node["funds"] + self.choice["cost"])
            intf.updatenode(tx, self.choice.end_node, "funds", self.choice.end_node["funds"] - payout)
            intf.updatenode(tx, node, "funds", node["funds"] + payout)
