from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))

with dri.session() as ses:
    ses.run("MATCH ()-[r]->() "
            "DELETE r")
    ses.run("MATCH (a) "
            "DELETE a")
    for i in range(6):
        ses.run("CREATE (a:Node {id:{id}, funds:10, payout:{id}})", id=i)
    for i in range(10):
        ses.run("CREATE (a:Agent {id:{id}, funds:10, switch:0.5})", id=i)
    ses.run("CREATE (a:Clock {time:0})")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=0 AND b.id=2 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=0 AND b.id=5 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=1 AND b.id=0 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=1 AND b.id=3 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=2 AND b.id=1 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=2 AND b.id=3 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=2 AND b.id=4 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=3 AND b.id=2 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=3 AND b.id=4 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=4 AND b.id=1 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=4 AND b.id=5 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Node), (b:Node) "
            "WHERE a.id=5 AND b.id=2 "
            "CREATE (a)-[r:REACHES {cost:5, outlook:b.id}]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=0 AND b.id=0 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=1 AND b.id=0 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=2 AND b.id=1 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=3 AND b.id=1 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=4 AND b.id=3 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=5 AND b.id=3 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=6 AND b.id=4 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=7 AND b.id=4 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=8 AND b.id=5 "
            "CREATE (a)-[r:LOCATED]->(b)")
    ses.run("MATCH (a:Agent), (b:Node) "
            "WHERE a.id=9 AND b.id=5 "
            "CREATE (a)-[r:LOCATED]->(b)")
