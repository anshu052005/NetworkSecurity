from pymongo import MongoClient
uri = "mongodb+srv://p20anshu05_db_user:JhJVnZBKwGPxwRQ6@cluster0.wzk4aoo.mongodb.net/"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)