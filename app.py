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


# @app.route("/")
# def index():
#     return render_template("index.html")


@app.route('/', methods=['GET', 'POST'])
def index():
    client = pymongo.MongoClient("mongodb://anshu92:VJkCopXqbK5smqf0@ds157349.mlab.com:57349/co_cluster",
                                 connectTimeoutMS=30000,
                                 socketTimeoutMS=None,
                                 socketKeepAlive=True)
    db = client.get_default_database()
    #
    collection = db['co_collection']
    errors = []
    pmcid = ''
    df = pd.DataFrame()
    title = ''
    if request.method == "POST":
        pmcid = request.form['pmcid']
        document = dict()
        try:
            document = collection.find_one({'pmcid': int(pmcid)})

        except Exception as e:
            print("Unexpected error: ", type(e), e)

        if document:
            co_table = document['co_table']
            co_table = sorted(co_table, key=itemgetter(1), reverse=True)
            labels = ['Word', 'Co-Occurrence']
            df = pd.DataFrame.from_records(co_table, columns=labels)
        if pmcid == '':
            title = ''
        elif not document:
            title = 'Document has no co-occurrence in the database.'
        else:
            title = "Co-occurrence for PMCID: " + pmcid

    return render_template('index.html', pmcids=[pmcid], errors=errors, tables=[df.to_html()], titles=['na', title])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
