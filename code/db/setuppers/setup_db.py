from cassandra.cluster import NoHostAvailable
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

import time as t

def fire_query(query):
    query = SimpleStatement(q)
    session.execute(query)

if __name__ == "__main__":

    t.sleep(30) # Let server setup the gossip
    
    start=t.time()

    session = None
    
    while session is None:
        try:
            cluster = Cluster(["172.18.0.1"],port=9042)#,auth_provider=auth_provider)
            session = cluster.connect()
        except NoHostAvailable:
            print("Database still not available, setupper waiting 10 seconds...")
            t.sleep(10)
        else:
            break
        
    q = "DROP KEYSPACE IF EXISTS bdp1"

    fire_query(q)
    
    q = '''CREATE KEYSPACE bdp1 WITH REPLICATION = {
             'class' : 'SimpleStrategy', 
             'replication_factor' : 3 };'''
    
    fire_query(q)

    q = '''CREATE TABLE IF NOT EXISTS bdp1.runs (
             id uuid,
             vendor_id bigint,
             pickup_dt timestamp,
             dropoff_dt timestamp,    
             passenger_count int,
             trip_distance float,
             rate_code_id int,
             store_and_fwd_flag boolean,
             pu_location_id bigint,
             do_location_id bigint,
             payment_type bigint,
             fare_amount float,
             extra float,
             mta_tax float,
             tip_amount float,
             tools_amount float,
             improvement_surcharge float,
             total_amount float,
             PRIMARY KEY ((pu_location_id), pickup_dt, dropoff_dt, id)
    ) WITH CLUSTERING ORDER BY (pickup_dt DESC);'''
    fire_query(q)
    
    stop=t.time()
    print("It took",stop-start,"(s)",sep=" ")

