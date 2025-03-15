from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Select database
db = client["bus_ticket_booking"]

# Print databases and collections
print("Databases:", client.list_database_names())  # Should include 'bus_ticket_booking'
print("Collections:", db.list_collection_names())  # Should include 'buses'

# Fetch some data from 'buses' collection
buses = list(db.buses.find())

print("\nSample Bus Data from MongoDB:")
for bus in buses:
    print(bus)
