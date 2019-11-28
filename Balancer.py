from neo4j import GraphDatabase

# TODO: Add nuid
class FlowReaction:

    def __init__(self, ruleset=None):
        self.uri = "bolt://localhost:7687"
        self.rules = ruleset

    def applyrules(self, tx):
        for rule in self.rules:
            tx.run(rule)


if __name__ == '__main__':
    rules = ["MATCH (n:Agent)-[r:LOCATED]->(m:Node) "
             "WHERE m.name='Hos' "
             "WITH n "
             "ORDER BY n.mob "
             "SKIP 4 "
             "LIMIT 1 "
             "WITH n.mob as lim "
             "MATCH (m:Node) "
             "WHERE m.name='Hos' "
             "SET m.discharged=lim "
             ]
    flowreaction = FlowReaction(rules)
    clock = 0
    while clock < 40:
        dri = GraphDatabase.driver(flowreaction.uri, auth=("dancer", "dancer"))
        with dri.session() as ses:
            ses.write_transaction(flowreaction.applyrules)
            res = ses.run("MATCH (a:Clock) "
                          "RETURN a.time")
        temp = res.values()
        clock = temp[0][0]
        print(clock)
        dri.close()
