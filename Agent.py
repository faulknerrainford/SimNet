from abc import ABC, abstractmethod


class Agent(ABC):

    def __init__(self, agentid, params=None, nuid = "id"):
        self.id = agentid
        self.view = None
        self.params = params
        self.choice = None
        self.nuid = nuid

    @abstractmethod
    def perception(self, tx, intf):
        self.view = intf.perception(tx, self.id)

    @abstractmethod
    def choose(self, tx, intf):
        self.perception(tx, intf)


    @abstractmethod
    def learn(self, tx, intf, choice):
        return [choice, tx, intf]
        # uses interface to update network based on choice

    @abstractmethod
    def payment(self, tx, intf):
        return None

    def move(self, tx, intf):
        self.choice = self.choose(tx, intf)
        if self.choice:
            # Move node based on choice using tx
            tx.run("MATCH (n:Agent)-[r:LOCATED]->() "
                   "WHERE n.id = {id} "
                   "DELETE r", id=self.id)
            new = self.choice.end_node[self.nuid]
            tx.run("MATCH (n:Agent), (a:Node) "
                   "WHERE n.id={id} AND a." + self.nuid + "={new} "
                   "CREATE (n)-[r:LOCATED]->(a)", id=self.id, new=new)
            self.payment(tx, intf)
            self.learn(tx, intf, self.choice)
