from flask import Flask
from flask import render_template
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
from operator import itemgetter
import cf_deployment_tracker
import os

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

port = int(os.getenv('PORT', 8080))


MONGODB_HOST = "mongodb://anshuman264:VJkCopXqbK5smqf0@cluster0-shard-00-00-ouybv.mongodb.net:27017,"
"cluster0-shard-00-01-ouybv.mongodb.net:27017,"
"cluster0-shard-00-02-ouybv.mongodb.net:27017/co_table?ssl=true&replicaSet=Cluster0-shard-0&authSource"
"=admin"
MONGODB_PORT = 27017
DBS_NAME = 'co_table'
COLLECTION_NAME = 'co_collection'


def todict(data):
    obj = dict()
    for key in data:
        if isinstance(data[key], ObjectId):
            print("Overflow - ", key, data[key])
        else:
            obj[key] = data[key]
    return obj


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/co_table/analysis")
def co_table():
    connection = MongoClient(
        "mongodb://anshuman264:VJkCopXqbK5smqf0@cluster0-shard-00-00-ouybv.mongodb.net:27017,"
        "cluster0-shard-00-01-ouybv.mongodb.net:27017,"
        "cluster0-shard-00-02-ouybv.mongodb.net:27017/co_table?ssl=true&replicaSet=Cluster0-shard-0&authSource"
        "=admin")

    collection = connection[DBS_NAME][COLLECTION_NAME]
    co_occurrences = collection.find_one()
    co_occurrences = todict(co_occurrences)
    co_list = list(co_occurrences.items())
    co_list = sorted(co_list, key=itemgetter(1), reverse=True)
    print(co_list)
    labels = ['Word', 'Co-Occurrence']

    df = pd.DataFrame.from_records(co_list, columns=labels)
    connection.close()

    return render_template("analysis.html", tables=[df.to_html()], titles=['na', 'of Research Articles'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
