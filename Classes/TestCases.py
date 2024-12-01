from pymongo import MongoClient

# Connection string
uri = "mongodb+srv://admin:admin@cluster0.ncwwi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def fetch_data():
    # Connect to MongoDB
    client = MongoClient(uri)
    try:
        # Access database and collection
        database = client['Testcases']
        collection = database['testcase']

        # Fetch all documents from the collection
        data = collection.find()
        for document in data:
            print(document)  # Print each document
    except Exception as e:
        print("Error fetching data:", e)
    finally:
        # Close the connection
        client.close()

# Call the function
fetch_data()
