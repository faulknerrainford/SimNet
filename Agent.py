from abc import ABC, abstractmethod


class Agent(ABC):

    def __init__(self, agentid, params=None):
        self.id = agentid
        self.view = None
        self.params = params
        self.choice = None

    @abstractmethod
    def choose(self, tx, intf):
        self.view = intf.perception(tx, self.id)
        edges = self.view[1:]
        validedges = []
        node = tx.run("MATCH (n:Dancer) "
                      "WHERE n.id = {id} "
                      "RETURN n", id=self.id).values()[0][0]
        for edge in edges:
            if edge["cost"] < node["funds"] and edge.end_node["payout"] < edge.end_node["funds"]:
                validedges = validedges + [edge]
        self.view[1:] = validedges

    @abstractmethod
    def learn(self, tx, intf, choice):
        return [choice, tx, intf]
        # uses interface to update network based on choice

    def move(self, tx, intf):
        self.choice = self.choose(tx, intf)
        if self.choice:
            self.learn(tx, intf, self.choice)
            # Move node based on choice using tx
            tx.run("MATCH (n:Dancer)-[r:LOCATED]->() "
                   "WHERE n.id = {id} "
                   "DELETE r", id=self.id)
            new = self.choice.end_node["id"]
            tx.run("MATCH (n:Dancer), (a:Node) "
                   "WHERE n.id={id} AND a.id={new} "
                   "CREATE (n)-[r:LOCATED]->(a)", id=self.id, new=new)
