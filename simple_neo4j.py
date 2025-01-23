from neo4j import GraphDatabase



def find_shortest_path(driver, start, end):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (source:City {name: $start}), (target:City {name: $end})
            CALL gds.shortestPath.dijkstra.stream({
              sourceNode: source,
              targetNode: target,
              relationshipProjection: {
                ROAD: {
                  type: 'ROAD',
                  properties: 'distance',
                  orientation: 'UNDIRECTED'
                }
              },
              nodeProjection: 'City',
              relationshipWeightProperty: 'distance'
            })
            YIELD totalCost, path
            RETURN totalCost, path
            """,
            start=start,
            end=end
        )

        for record in result:
            total_cost = record["totalCost"]
            path_nodes = [node["name"] for node in record["path"].nodes]  # Extract city names
            print(f"Shortest path from {start} to {end}: {path_nodes} (Distance: {total_cost} km)")
            return path_nodes, total_cost  # Return path and distance

    return None, None


from neo4j import GraphDatabase

def main():
    URI = 'bolt://localhost:7687'
    AUTH = ('neo4j', 'nowehaselko123')
    driver = None
    
    try:
        driver = GraphDatabase.driver(uri=URI, auth=AUTH)
        print('Connected to Neo4j successfully!')

        with driver.session() as session:
            for _ in range(10):
                name, name2, distance = input('City1, City2, distance: ').split()
                distance = float(distance)
                
                session.run(
                    'MERGE (:City {name:$name})',
                    name=name
                )
                session.run(
                    'MERGE (:City {name:$name2})',
                    name2=name2
                )
                session.run(
                    'MATCH (a:City {name:$name}), (b:City {name:$name2}) '
                    'MERGE (a)-[:ROAD {distance:$distance}]->(b)',
                    name=name,
                    name2=name2,
                    distance=distance
                )
                print(f'Added: {name}-{distance}->{name2}')

            for _ in range(5):
                name, name2 = input('City1, City2: ').split()
                find_shortest_path(driver, name, name2)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        if driver:
            driver.close()

if __name__ == '__main__':
    main()