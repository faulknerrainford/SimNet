from neo4j import GraphDatabase
from Interface import Interface
from Fall_agent import FallAgent


def countactiveagents(tx):
    total_agents = tx.run("MATCH (n:Agent) ""WITH n ""RETURN count(*)").value()[0]
    care_agents = tx.run("MATCH (n:Agent)-[r:LOCATED]->(a:Node) ""WHERE a.name='Care' ""RETURN count(*)").value()[0]
    return total_agents-care_agents


def countindagents(tx):
    ind_agents = tx.run("MATCH (n:Agent)-[r:LOCATED]->(a:Node) ""WHERE a.name='Ind' ""RETURN count(*)").value()[0]
    return ind_agents


if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    intf = Interface()
    clock = 0
    fa = FallAgent(None)
    while clock < 40:
        with dri.session() as ses:
            active = ses.read_transaction(countactiveagents)
            ind = ses.read_transaction(countindagents)
            if ind < 10 and active - ind < 10:
                for i in range(max(10 - ind, 10 - (active - ind))):
                    ses.write_transaction(fa.generator, intf, [0.8, 0.9, 1])
            clock = ses.run("MATCH (a:Clock) "
                            "RETURN a.time").values()[0][0]
        print(clock)
    dri.close()
