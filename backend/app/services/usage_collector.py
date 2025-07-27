import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models, database
from app.services.flussonic import FlussonicService

def collect_usage_data():
    """
    This function is intended to be run as a periodic background job.
    It fetches traffic data for all streams on all registered servers.
    """
    print("Starting traffic data collection...")
    db: Session = next(database.get_db())
    
    servers = db.query(models.FlussonicServer).all()
    if not servers:
        print("No Flussonic servers configured. Exiting.")
        return

    # We want to get data for the last 24 hours.
    # Flussonic's 'from' parameter expects a Unix timestamp in seconds.
    start_time = int((datetime.utcnow() - timedelta(days=1)).timestamp())

    for server in servers:
        print(f"Processing server: {server.name} ({server.url})")
        try:
            flussonic_service = FlussonicService(
                server_url=server.url,
                username=server.username,
                password=server.password
            )
            
            # Get all streams on the server
            streams_on_server = flussonic_service.get_streams()
            stream_names = [s['name'] for s in streams_on_server if 'name' in s]

            if not stream_names:
                print(f"No streams found on server {server.name}.")
                continue

            # Fetch traffic report for all streams on this server
            traffic_data = flussonic_service.get_traffic_report(stream_names, start_time)

            # The report returns data per stream
            for stream_name, usage_list in traffic_data.items():
                for usage_record in usage_list:
                    # 'usage_record' is a tuple: [timestamp_ms, bytes]
                    record_time = datetime.utcfromtimestamp(usage_record[0] / 1000)
                    bytes_used = usage_record[1]

                    # Check if this record already exists to avoid duplicates
                    existing_record = db.query(models.TrafficUsage).filter(
                        models.TrafficUsage.stream_name == stream_name,
                        models.TrafficUsage.server_id == server.id,
                        models.TrafficUsage.timestamp == record_time
                    ).first()

                    if not existing_record:
                        new_usage = models.TrafficUsage(
                            server_id=server.id,
                            stream_name=stream_name,
                            bytes_used=bytes_used,
                            timestamp=record_time
                        )
                        db.add(new_usage)

            db.commit()
            print(f"Successfully collected traffic data for server: {server.name}")

        except Exception as e:
            print(f"Error processing server {server.name}: {e}")
            db.rollback() # Rollback changes for the failed server

    print("Traffic data collection finished.")

if __name__ == "__main__":
    # This allows running the script directly for testing
    collect_usage_data()
