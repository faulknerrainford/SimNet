from neo4j import GraphDatabase
from random import randrange


def setup(tx):
    res = tx.run("MATCH (a)-[:REACHES]->(b) "
                 "RETURN a.id, b.id")
    res = res.values()
    for edge in res:
        tx.run("MATCH (a)-[r:REACHES]->(b) "
               "WHERE a.id = {a} AND b.id = {b} "
               "SET r.cost = {cost}", a=edge[0], b=edge[1], cost=randrange(0, 6))
    tx.run("MATCH (n:Dancer) "
           "SET n.funds = 10")
    tx.run("MATCH (n:Node) "
           "SET n.funds = 10")
    tx.run("MATCH (c:Clock) "
           "SET c.time = 0")


if __name__ == '__main__':
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("dancer", "dancer"))
    with driver.session() as ses:
        tx = ses.write_transaction(setup)
    driver.close()
