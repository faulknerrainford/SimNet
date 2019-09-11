from neo4j import GraphDatabase


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


if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    with dri.session() as ses:
        tx = ses.begin_transaction()
        res = tx.run("MATCH (n:Dancer)-[:LOCATED]->(a) "
                     "WITH n, a "
                     "ORDER BY n.id "
                     "RETURN n.id, a.id")
        tx.close()
        results = res.values()
        agents = [Dancer(ag[0]) for ag in results]
        clock = 0
        while clock < 2000:
            for agent in agents:
                ses.write_transaction(agent.process, verbose)
            res = ses.run("MATCH (a:Clock) "
                          "SET a.time = a.time + 1 "
                          "RETURN a.time")
            temp = res.values()
            clock = temp[0][0]
            print("T: " + clock.__str__())
    dri.close()
