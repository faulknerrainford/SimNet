from neo4j import GraphDatabase


class FlowReaction:

    def __init__(self, ruleset=None):
        self.uri = "bolt://localhost:7687"
        self.rules = ruleset

    def applyrules(self, tx):
        for rule in self.rules:
            tx.run(rule)


if __name__ == '__main__':
    rules = ["MATCH ()-[:LOCATED]->(a) "
             "WITH a, count(*) AS num "
             "WHERE num > 2 "
             "MATCH (a)-[r:REACHES]->() "
             "WHERE r.cost > 0 "
             "SET r.cost = r.cost - 1",
             "MATCH (a)-[:LOCATED]->(a) "
             "WITH a, count(*) AS num "
             "WHERE num < 1 "
             "MATCH ()-[r:REACHES]->(a) "
             "WHERE r.cost > 0 "
             "SET r.cost = r.cost - 1",
             "MATCH ()-[:LOCATED]->(a) "
             "WITH a, count(*) AS num "
             "WHERE num < 1 "
             "MATCH ()-[r:REACHES]->(a) "
             "WHERE r.cost > 0 "
             "SET r.cost = r.cost - 1",
             "MATCH (a:Node) "
             "WITH a "
             "WHERE a.funds < a.payout "
             "MATCH (a)-[r:REACHES]->() "
             "WHERE r.cost < 160 "
             "SET r.cost = r.cost + 1",
             "MATCH ()-[:LOCATED]->(a:Node)  "
             "WITH a, count(*) AS num "
             "WHERE a.funds < a.payout AND num < 1 "
             "SET a.payout = a.payout - 1",
             "MATCH (a:Node) "
             "WHERE a.funds > 2*a.payout "
             "SET a.payout = a.payout + 1"
             ]
    flowreaction = FlowReaction(rules)
    clock = 0
    while clock < 2000:
        dri = GraphDatabase.driver(flowreaction.uri, auth=("dancer", "dancer"))
        with dri.session() as ses:
            ses.write_transaction(flowreaction.applyrules)
            res = ses.run("MATCH (a:Clock) "
                          "RETURN a.time")
        temp = res.values()
        clock = temp[0][0]
        print(clock)
        dri.close()
