from neo4j import GraphDatabase
from Fall_agent import FallAgent
from Interface import Interface

uri = "bolt://localhost:7687"
dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))

with dri.session() as ses:
    # Clear existing graph
    ses.run("MATCH ()-[r]->() "
            "DELETE r")
    ses.run("MATCH (a) "
            "DELETE a")
    # Create network nodes
    ses.run("CREATE (a:Node {name:'Ind'})")
    ses.run("CREATE (a:Node {name:'Hos', energy:0.2})")
    # ses.run("CREATE (a:Node {name:HosTP, energy:-0.6})")
    ses.run("CREATE (a:Node {name:'Home', energy:0.4})")
    ses.run("CREATE (a:Node {name:'Social', energy:-0.4, modm:0.1, modc:0.3, modrc:0.4})")
    ses.run("CREATE (a:Node {name:'TP', energy:-0.8, modm:0.5, modc:0.2})")
    ses.run("CREATE (a:Node {name:'Care'})")
    ses.run("CREATE (a:Node {name:'Resource', energy:-0.5, modrm:0.6})")
    # Paths between nodes
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Ind' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0 , mobility:1, confidence:1, modm:-0.4, modc:-0.6}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Hos' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.2, "
            "energy:0.1, worth: 0}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Hos' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0.1, mobility:1, confidence:1, energy:-0.1, worth:0.1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.1, worth:0}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Social' "
            "CREATE (a)-[r:REACHES {effort:0.3, mobility:0.6, confidence:0.4, worth:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Social' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, worth:0}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='TP' "
            "CREATE (a)-[r:REACHES {effort:0.8, mobility:0.5, confidence:0.5, worth:2}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='TP' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, worth:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Resource' "
            "CREATE (a)-[r:REACHES {effort:0.3, mobility:0.4, confidence:0.6, worth:2}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Resource' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, worth:0}]->(b)")
    # Falls
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Resource' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.8, modc:-0.6}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='TP' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.8, modc:-0.6}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Social' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.8, modc:-0.6}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.8, modc:-0.3}]->(b)")
    # Declare a fall agent with a None id and use it to generate a set of agents into the system
    fa = FallAgent(None)
    intf = Interface()
    for i in range(10):
        ses.write_transaction(fa.generator, intf, [0.8, 0.9, 1])
