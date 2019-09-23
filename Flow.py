from neo4j import GraphDatabase
from Dancers import Dancer

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
