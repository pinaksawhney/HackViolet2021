import boto3
import base64
import json
from flask_cors import CORS, cross_origin
from googlesearch import search
from airtable import Airtable
from random import randrange
from flask import Flask, request

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class Worker:
    unique = 0
    isAuth = False
    userInfoTable = Airtable('appKGveLcvfcFaftJ', "UserInfo", "key1B3UuMtQpUkWQS")
    designProjectTable = Airtable('appKGveLcvfcFaftJ', "UserProfile", "key1B3UuMtQpUkWQS")


@app.route("/")
@cross_origin()
def index():
    """Present some documentation"""
    return "<h2>Add API documentation here !!</h2>"


@app.route("/get_homepage/query=<string:q>")
@cross_origin()
def get_homepage(q):
    search_results = []
    for i in search(q, tld="com", num=10, stop=10, pause=1):
        search_results.append(i)
    return json.dumps(search_results)


@app.route("/get_resources/")
@cross_origin()
def get_resources():
    pass


def upload_to_s3(filename):
    s3 = boto3.client('s3')
    s3.upload_file(filename, 'sigmoidhack', filename)


def make_attachment(url):
    return [{'url': url}]


@app.route("/post_profile/", methods=['POST'])
@cross_origin()
def post_profile():
    username = request.json['UserName']
    first = request.json['FirstName']
    last = request.json['LastName']
    bio = request.json['Bio']
    photo = request.json['Photo']
    chat = request.json['ChatGroup']
    interest = request.json['Interests']

    if Worker.isAuth:
        filename = ""
        if photo:
            imgData = base64.b64decode(photo)
            filename = username + str(Worker.unique) + str(randrange(1000000)) + ".jpg"
            Worker.unique += 1
            with open(filename, 'wb') as f:
                f.write(imgData)
        upload_to_s3(filename)
        url = "https://sigmoidhack.s3.amazonaws.com/" + filename
        Worker.designProjectTable.insert({"FirstName": first, "UserName": username, "LastName": last, "Bio": bio,
                                          "ChatGroup": chat, "Interests": interest, "Photo": make_attachment(url)})
        return {"Success": True}
    return {"Success": False}


@app.route("/get_profile/username=<string:username>")
@cross_origin()
def get_profile(username):
    profile = {}
    if Worker.isAuth:
        record = Worker.designProjectTable.search('UserName', str(username))[0]["fields"]
        chatGroups = record["ChatGroup"].split(',')
        interests = record["Interests"].split(',')
        profile = {"UserName": record["UserName"], "Bio": record["Bio"], "FirstName": record["FirstName"],
                   "LastName": record['LastName'], "ChatGroup": chatGroups, "Interests": interests,
                   "Photo": record["Photo"][0]["url"]
                   }
    return json.dumps(profile)


@app.route("/post_signup/", methods=['POST'])
@cross_origin()
def post_signup():
    username = request.json['Username']
    password = request.json['Password']
    confirm_password = request.json['Confirm Password']
    email = request.json['EmailID']
    if confirm_password != password or Worker.userInfoTable.search("EmailID", str(email)):
        return {"Success": False}
    if not Worker.userInfoTable.search("Username", str(username)):
        Worker.userInfoTable.insert({"Username": str(username), "Password": str(password), "Active": True,
                                     "EmailID": str(email)})
        return {"Success": True}
    return {"Success": False}


@app.route("/post_login/", methods=['POST'])
@cross_origin()
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
@cross_origin()
def post_deleteAccount():
    username = request.json['Username']
    password = request.json['Password']
    if Worker.userInfoTable.search("Username", str(username)) and Worker.userInfoTable.search("Password",
                                                                                              str(password)):
        Worker.userInfoTable.delete_by_field("Username", username)
        # ToDo- delete user account history from DB
        return {"Success": True}
    return {"Success": False}


"""
Main Routine
"""
if __name__ == "__main__":
    app.run()


# https://hackviolet21.herokuapp.com/
