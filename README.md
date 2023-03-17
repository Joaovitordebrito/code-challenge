# project set-up

 - run the command 'docker compose up' to fire up the neo4j database and airflow
 - to connect to the neo4j console go to localhost:7888
    - the neo4j crendentials are 'neo4j/password'
    - the connection url should be localhost:7999
 - the airflow url are http://localhost:8080/ and the credentials are 'airflow/airflow'

 - On the src directory run the follow command: python3 extract_data.py
 - it should create a graph similar to the reference image on the neo4j database 
 