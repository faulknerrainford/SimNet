from neo4j import GraphDatabase


def applychange(tx, method="drop"):
    result = tx.run("MATCH (n:Node) "
                    "WHERE NOT ()-[:LOCATED]->(n) "
                    "RETURN n.id").values()
    if result:
        result = result[0]
        if len(result) > 1:
            idlist = [ids[0] for ids in result]
        else:
            idlist = [result[0]]
        if idlist:
            for ids in idlist:
                if method == "drop":
                    tx.run("MATCH (n:Node)-[r]->() "
                           "WHERE n.id={id} "
                           "DELETE r ", id=ids)
                    tx.run("MATCH ()-[r]->(n:Node) "
                           "WHERE n.id={id} "
                           "DELETE r ", id=ids)
                    tx.run("MATCH (n:Node) "
                           "WHERE n.id={id} "
                           "DELETE (n)", id=ids)
                elif method == "through":
                    tx.run("MATCH (n:Node) "
                           "WHERE n.id={id} "
                           "WITH n "
                           "MATCH (a:Node)-[r:REACHES]->(n:Node) "
                           "WITH n, a, r.cost as acost "
                           "MATCH (n:Node)-[s:REACHES]->(b:Node) "
                           "WITH n, a, b, acost, s.cost as bcost "
                           "CREATE (a)-[t:REACHES, {cost:(acost+bcost)/2}]->(b)", id=ids)
                    tx.run("MATCH (n:Node)-[r:REACHES]->() "
                           "WHERE n.id={id} "
                           "DELETE r", id=ids)
                    tx.run("MATCH ()-[r:REACHES]->(n:Node) "
                           "WHERE n.id={id} "
                           "DELETE r", id=ids)


if __name__ == '__main__':
    clock = 0
    while clock < 2000:
        uri = "bolt://localhost:7687"
        dri = GraphDatabase.driver(uri, auth=("monitor", "monitor"))
        with dri.session() as ses:
            ses.write_transaction(applychange)
            res = ses.run("MATCH (a:Clock) "
                          "RETURN a.time")
        temp = res.values()
        clock = temp[0][0]
        print(clock)
        dri.close()
