class Dancer:

    def __init__(self, identity):
        self.id = identity
        self.avfunds = None
        self.cnode = None

    def process(self, tx, verbose=False):
        update = tx.run("MATCH (n:Dancer)-[:LOCATED]->(a:Node) "
                        "WHERE n.id = {id} "
                        "RETURN n.funds, a.id", id=self.id)
        [self.avfunds, self.cnode] = update.values()[0]
        print("Dancer at node: "+self.cnode.__str__() + " with funds: " + self.avfunds.__str__()) if \
            verbose else None
        print("Processing Dancer: "+self.id.__str__()) if verbose else None
        result = tx.run("MATCH (a:Node)-[r:REACHES]->(b:Node) "
                        "WHERE a.id = {current} AND b.funds>=b.payout AND r.cost<= {budget} "
                        "WITH a, r, b "
                        "ORDER BY r.cost "
                        "RETURN r.cost, b.id, b.payout", current=self.cnode, budget=self.avfunds)
        next_nodes = result.values()
        if next_nodes:
            [cost, nnode, ben] = next_nodes[0]
            print("Next node id: " + nnode.__str__()) if verbose else None
            tx.run("MATCH (a:Node), (b:Dancer) "
                   "WHERE a.id = {next} AND b.id = {id} "
                   "CREATE (b)-[:LOCATED]->(a)", next=nnode, id=self.id)
            tx.run("MATCH (b:Dancer)-[r:LOCATED]->(a:Node) "
                   "WHERE a.id = {current} AND b.id = {id} "
                   "DELETE r", current=self.cnode, id=self.id)
            tx.run("MATCH (b:Dancer) "
                   "WHERE b.id = {id} "
                   "SET b.funds = b.funds - {cost}", cost=cost, id=self.id)
            tx.run("MATCH (b:Dancer) "
                   "WHERE b.id = {id} "
                   "SET b.funds = b.funds + {benefit}", benefit=ben, id=self.id)
            tx.run("MATCH (a:Node) "
                   "WHERE a.id = {current} "
                   "SET a.funds = a.funds + {cost}", current=self.cnode, cost=cost)
            tx.run("MATCH (a:Node) "
                   "WHERE a.id = {next} "
                   "SET a.funds = a.funds - {benefit}", next=nnode, benefit=ben)
            self.cnode = nnode
