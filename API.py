import boto3
import base64
import json
from airtable import Airtable
from flask import Flask, request

app = Flask(__name__)


class Worker:
    unique = 0
    isAuth = False
    userInfoTable = Airtable('appKGveLcvfcFaftJ', "UserInfo", "key1B3UuMtQpUkWQS")
    designProjectTable = Airtable('appKGveLcvfcFaftJ', "TrialEnrollment", "key1B3UuMtQpUkWQS")


@app.route("/")
def index():
    """Present some documentation"""
    return "<h2>Add API documentation here !!</h2>"


@app.route("/recommendation_from_ml/JournalText=<string:JournalText>&Title=<string:Title>")
def recommendation_from_ml(JournalText, Title):
    # ToDo - recommendation system based on text and title
    return {'Activities': ['Hiking', 'Basketball', 'Swimming', 'Workout'], 'Groups':
        ['Travel and Tourism', 'Sports and Recreation', 'Gym and Fitness'], 'Resources':
                ['World Health organization https://www.who.int/health-topics/mental-health#tab=tab_1',
                 'CDC https://www.cdc.gov/mentalhealth/index.htm',
                 'Psychological health https://www.mentalhealth.gov/basics/what-is-mental-health']}


def upload_to_s3(filename):
    s3 = boto3.client('s3')
    s3.upload_file(filename, 'sigmoidhack', filename)


def make_attachment(url):
    return [{'url': url}]


@app.route("/post_journal/", methods=['POST'])
def post_journal():
    title = request.json['title']
    date = request.json['date']
    username = request.json['username']
    userID = 5
    journalText = request.json['journalText']
    journalImage = request.json['journalImage']

    if Worker.isAuth:
        filename = ""
        if journalImage:
            imgData = base64.b64decode(journalImage)
            # filename = username + str(Worker.unique) + str(randrange(1000000)) + ".jpg"
            Worker.unique += 1
            with open(filename, 'wb') as f:
                f.write(imgData)
        # mood = mood_from_ml(journalText, title)
        upload_to_s3(filename)
        url = "https://sigmoidhack.s3.amazonaws.com/" + filename
        # Worker.designProjectTable.insert({"UserID": userID, "UserName": username, "Date": date, "Title": title,
        #                                  "JournalText": journalText, "JournalImage": make_attachment(url),
        #                                  "Mood": mood})
        return {"Success": True}
    return {"Success": False}


@app.route("/get_all_journals/username=<string:username>")
def get_all_journals(username):
    all_journals = []
    if Worker.isAuth:
        records = Worker.designProjectTable.search('UserName', str(username))
        for r in records:
            img = ""
            if "JournalImage" in r["fields"].keys():
                img = r["fields"]["JournalImage"][0]["url"]
            curr = {"JournalID": r["fields"]["JournalID"], "Mood": r["fields"]["Mood"], "UserID": r["fields"]["UserID"],
                    "Title": r["fields"]["Title"], "UserName": r["fields"]["UserName"], "JournalImage": img,
                    "JournalText": r["fields"]["JournalText"], "Date": r["fields"]["Date"]}
            all_journals.append(curr)
    return json.dumps(all_journals)


@app.route("/get_single_journal/<int:journalID>")
def get_single_journal(journalID):
    journal = {}
    if Worker.isAuth:
        fetched_journal = Worker.designProjectTable.search("JournalID", journalID)
        journal = fetched_journal[0]["fields"]
    return journal


@app.route("/post_signup/", methods=['POST'])
def post_signup():
    username = request.json['Username']
    password = request.json['Password']
    facebook = request.json['Facebook']
    google = request.json['Google']
    if not Worker.userInfoTable.search("Username", str(username)):
        Worker.userInfoTable.insert({"Username": str(username), "Password": str(password), "Active": True})
        return {"Success": True}
    return {"Success": False}


@app.route("/post_login/", methods=['POST'])
def post_login():
    # ToDo - FB and Google Auth login
    username = request.json['Username']
    password = request.json['Password']
    facebook = request.json['Facebook']
    google = request.json['Google']
    if Worker.userInfoTable.search("Username", str(username)) \
            and Worker.userInfoTable.search("Password", str(password)):
        Worker.isAuth = True
    else:
        Worker.isAuth = False
    return {"Success": Worker.isAuth}


@app.route("/delete_account/", methods=['POST'])
def post_deleteAccount():
    username = request.json['Username']
    password = request.json['Password']
    if Worker.userInfoTable.search("Username", str(username)) and Worker.userInfoTable.search("Password", str(password)):
        Worker.userInfoTable.delete_by_field("Username", username)
        # ToDo - delete user account history from DB
        return {"Success": True}
    return {"Success": False}


"""
Main Routine
"""
if __name__ == "__main__":
    app.run()
