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
    ses.run("CREATE (a:Clock {time:0})")
    ses.run("CREATE (a:Node {name:'Ind'})")
    ses.run("CREATE (a:Node {name:'Hos', energy:0.2, discharged:0.8})")
    ses.run("CREATE (a:Node {name:'Home', energy:0.3})")
    ses.run("CREATE (a:Node {name:'Social', energy:-0.4, modm:0.05, modc:0.2, modrc:0.2})")
    ses.run("CREATE (a:Node {name:'PT', energy:-0.8, modm:0.3, modc:0.3})")
    ses.run("CREATE (a:Node {name:'Care', time:'t'})")
    ses.run("CREATE (a:Node {name:'Resource', energy:-0.5, modrm:0.2})")
    ses.run("CREATE (a:Node {name:'GP'})")
    # Paths between nodes
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Ind' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES { worth: -10, effort:0 , mobility:1, confidence:1, modm:-0.2, modc:-0.1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Hos' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.05, "
            "energy:0.1, worth: 0}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Hos' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0.01, mobility:1, confidence:1, energy:-0.1, worth:0.1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, modm:-0.015, modc:-0.02, worth:0}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Ind' AND b.name='GP' "
            "CREATE (a)-[r:REACHES {worth:-5, effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.025}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='GP' "
            "CREATE (a)-[r:REACHES {worth:-5, effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.025}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='PT' AND b.name='GP' "
            "CREATE (a)-[r:REACHES {worth:-5, effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.025}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Social' AND b.name='GP' "
            "CREATE (a)-[r:REACHES {worth:-5, effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.025}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Resources' AND b.name='GP' "
            "CREATE (a)-[r:REACHES {worth:-5, effort:0, mobility:1, confidence:1, modm:-0.1, modc:-0.025}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='GP' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='GP' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='GP' AND b.name='PT' "
            "CREATE (a)-[r:REACHES {effort:0.3, mobility:1, confidence:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Social' "
            "CREATE (a)-[r:REACHES {effort:0.1, mobility:0.6, confidence:0.4, worth:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Social' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, worth:0}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='PT' "
            "CREATE (a)-[r:REACHES {effort:0.3, mobility:0.5, confidence:0.5, worth:2}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='PT' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, worth:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Resource' "
            "CREATE (a)-[r:REACHES {effort:0.4, mobility:0.4, confidence:0.6, worth:2}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Resource' AND b.name='Home' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, worth:0}]->(b)")
    # Falls
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Resource' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.25, modc:-0.35}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='PT' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.25, modc:-0.35}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Social' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.25, modc:-0.35}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Hos' "
            "CREATE (a)-[r:REACHES {effort:0, mobility:1, confidence:1, energy: -0.8, modm:-0.25, modc:-0.5}]->(b)")
    ses.run("MATCH (a) "
            "WHERE a.name = 'Ind' "
            "CREATE (a)-[r:REACHES { worth:0, effort:0, mobility:1, confidence:1, energy: 0, modm:-0.00018}]->(a)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Ind' "
            "CREATE (a)-[r:REACHES {effort:1, worth:-1, mobility:1, confidence:1, "
            "energy: 0.2, modm:0, modc:0.4}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Home' AND b.name='Care' "
            "CREATE (a)-[r:REACHES {effort:0, worth:-1, mobility:1, confidence:1}]->(b)")
    ses.run("MATCH (a), (b) "
            "WHERE a.name='Hos' AND b.name='Care' "
            "CREATE (a)-[r:REACHES {effort:0, worth:-100, mobility:1, confidence:1}]->(b)")
    # Declare a fall agent with a None id and use it to generate a set of agents into the system
    fa = FallAgent(None)
    intf = Interface()
    for i in range(10):
        ses.write_transaction(fa.generator, intf, [0.8, 0.9, 1])
dri.close()
