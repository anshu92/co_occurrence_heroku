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

MONGODB_HOST = "mongodb://anshu92:VJkCopXqbK5smqf0@ds157349.mlab.com:57349/co_cluster"
MONGODB_PORT = 57349
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
def co_table():
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
            document = collection.find_one({'pmcid': pmcid})

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
