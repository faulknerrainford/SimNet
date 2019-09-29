from abc import ABC, abstractmethod


class Agent(ABC):

    def __init__(self, agentid, params=None):
        self.id = agentid
        self.view = None
        self.params = params

    @abstractmethod
    def choose(self, tx, intf):
        self.view = intf.perception(tx, self.id)
        # node = self.view[0]
        # edges = self.view[1:]
        # choose edge and return value
        # (might change to handing the whole edge around to keep end node info)
        # for now we return 0 indicating we take the first edge
        # mincost = 60
        # choice = None
        # for edge in edges:
        #     if edge[cost]<mincost:
        #         mincost = edge[cost]
        #         choice = edge
        # return choice

    @abstractmethod
    def learn(self, tx, intf, choice):
        return [choice, tx, intf]
        # uses interface to update network based on choice

    def move(self, tx, intf):
        choice = self.choose(tx, intf)
        self.learn(tx, intf, choice)
        # Move node based on choice using tx
        tx.run("MATCH (n)-[r:LOCATED]->() "
               "WHERE n.id = {id} "
               "DELETE (n)-[r:LOCATED]->()", id=self.id)
        new = choice.end_node["id"]
        tx.run("MATCH (n) (a) "
               "WHERE n.id={id} AND a.id={new} "
               "CREATE (n)-[r:LOCATED]->(a)", id=self.id, new=new)
