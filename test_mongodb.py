
from pymongo import MongoClient

uri = "mongodb+srv://p20anshu05_db_user:<db_password>@cluster0.av5wxkj.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)