from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))

with dri.session() as ses:
    ses.run("MATCH ()-[r]->() "
            "DELETE r")
    ses.run("MATCH (a) "
            "DELETE a")
    ses.run("CREATE (a:Node {name:Ind})")
    ses.run("CREATE (a:Node {name:Hos, energy:0.2})")
    # ses.run("CREATE (a:Node {name:HosTP, energy:-0.6})")
    ses.run("CREATE (a:Node {name:Home, energy:0.4})")
    ses.run("CREATE (a:Node {name:Social, energy:-0.4, modm:0.1, modc:0.3, modrc:0.4})")
    ses.run("CREATE (a:Node {name:TP, energy:-0.8, modm:0.5, modc:0.2})")
    ses.run("CREATE (a:Node {name:Care})")
    ses.run("CREATE (a:Node {name:Resource, energy-0.5, modrm:0.6})")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Ind and b.name=Hos "
            "CREATE (a)-[r:REACHES {effort:0 , mobility:1, confidence:1, modm:-0.4, modc:-0.6}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Hos and b.name=Hos "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.2, "
            "energy:0.1}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Hos and b.name=Home "
            "CREATE (a)-[r:REACHES {effort:0.1, mobility:1, confidence:1, energy:-0.1}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Home and b.name=Home "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.1}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Home and b.name=Social "
            "CREATE (a)-[r:REACHES {effort:0.3, mobility:0.6, confidence:0.4}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Social and b.name=Home "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Home and b.name=TP "
            "CREATE (a)-[r:REACHES {effort:0.8, mobility:0.5, confidence:0.5}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=TP and b.name=Home "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Home and b.name=Resource "
            "CREATE (a)-[r:REACHES {effort:0.3, mobility:0.4, confidence:0.6}]->(b)")
    ses.run("MATCH (a) (b) "
            "WHERE a.name=Resource and b.name=Home "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1}]->(b)")
