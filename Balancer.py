from neo4j import GraphDatabase


class FlowReaction:

    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.rules = ["MATCH ()-[:LOCATED]->(a) "
                      "WITH a, count(*) AS load "
                      "WHERE load > 2 "
                      "MATCH (a)-[r:REACHES]->() "
                      "WHERE r.cost > 0 "
                      "SET r.cost = r.cost - 1",
                      "MATCH (a)-[:LOCATED]->(a) "
                      "WITH a, count(*) AS load "
                      "WHERE load < 1 "
                      "MATCH ()-[r:REACHES]->(a) "
                      "WHERE r.cost > 0 "
                      "SET r.cost = r.cost - 1",
                      "MATCH ()-[:LOCATED]->(a) "
                      "WITH a, count(*) AS load "
                      "WHERE load < 1 "
                      "MATCH ()-[r:REACHES]->(a) "
                      "WHERE r.cost > 0 "
                      "SET r.cost = r.cost - 1",
                      "MATCH (a:Node) "
                      "WITH a "
                      "WHERE a.funds < a.payout "
                      "MATCH (a)-[r:REACHES]->() "
                      "WHERE r.cost < 160 "
                      "SET r.cost = r.cost + 1", "MATCH ()-[:LOCATED]->(a:Node)  "
                      "WITH a, count(*) AS load"
                      "WHERE a.funds < a.payout AND load < 1 "
                      "SET a.payout = a.payout - 1",
                      "MATCH (a:Node) "
                      "WHERE a.funds > 2*a.payout "
                      "SET a.payout = a.payout + 1"
                      ]

    def applyrules(self):
        driver = GraphDatabase.driver(self.uri, auth=("monitor", "monitor"))
        with driver.session() as session:
            for rule in self.rules:
                session.run(rule)
        driver.close()


if __name__ == '__main__':
    flowreaction = FlowReaction()
    clock = 0
    while clock < 2000:
        flowreaction.applyrules()
        dri = GraphDatabase.driver(flowreaction.uri, auth=("monitor", "monitor"))
        with dri.session() as ses:
            res = ses.run("MATCH (a:Clock) "
                          "RETURN a.time")
        temp = res.values()
        clock = temp[0][0]
        print(clock)
        dri.close()
