from neo4j import GraphDatabase


def applychange(tx, type="drop"):
    id = tx.run("MATCH (n) "
                "WHERE NOT ()-[:LOCATED]->(n) "
                "RETURN n.id").values()[0]
    if type == "drop":
        tx.run("MATCH (n) "
               "WHERE n.id={id} "
               "DELETE (n)-[]->() ", id=id)
        tx.run("MATCH (n) "
               "WHERE n.id={id} "
               "DELETE ()-[]->(n) ", id=id)
        tx.run("MATCH (n) "
               "WHERE n.id={id} "
               "DELETE (n)", id=id)
    elif type == "through":
        tx.run("MATCH (n) "
               "WHERE n.id={id} "
               "WITH n "
               "MATCH (a)-[r:REACHES]->(n) "
               "WITH n, a, r.cost as acost "
               "MATCH (n)-[s:REACHES]->(b) "
               "WITH n, a, b, acost, s.cost as bcost "
               "CREATE (a)-[t:REACHES, {cost:(acost+bcost)/2}]->(b)", id=id)
        tx.run("MATCH (n)-[r:REACHES]->() "
               "WHERE n.id={id} "
               "DELETE r", id=id)
        tx.run("MATCH ()-[r:REACHES]->(n) "
               "WHERE n.id={id} "
               "DELETE r", id=id)


if __name__ == '__main__':
    clock = 0
    while clock < 2000:
        dri = GraphDatabase.driver(flowreaction.uri, auth=("monitor", "monitor"))
        with dri.session() as ses:
            ses.write_transition(applychange)
            res = ses.run("MATCH (a:Clock) "
                          "RETURN a.time")
        temp = res.values()
        clock = temp[0][0]
        print(clock)
        dri.close()
