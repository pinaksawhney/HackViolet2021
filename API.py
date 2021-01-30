import boto3
import base64
import json

from googlesearch import search
from airtable import Airtable
from random import randrange
from flask import Flask, request

app = Flask(__name__)


class Worker:
    unique = 0
    isAuth = False
    userInfoTable = Airtable('appKGveLcvfcFaftJ', "UserInfo", "key1B3UuMtQpUkWQS")
    designProjectTable = Airtable('appKGveLcvfcFaftJ', "UserProfile", "key1B3UuMtQpUkWQS")


@app.route("/")
def index():
    """Present some documentation"""
    # https://hackviolet21.herokuapp.com/
    # https://airtable.com/tbl3eJHHpfoyoFGnH/viwGYBQerAsvmawbm?blocks=hide
    # https://s3.console.aws.amazon.com/s3/buckets/sigmoidhack?region=us-east-1&tab=objects
    return "<h2>Add API documentation here !!</h2>"


@app.route("/get_homepage/query=<string:q>")
def get_homepage(q):
    search_results = []
    for i in search(q, tld="com", num=10, stop=10, pause=1):
        search_results.append(i)
    return json.dumps(search_results)


@app.route("/get_groups/user=<string:user>")
def get_groups(user):
    groups = []
    if Worker.isAuth:
        record = Worker.designProjectTable.search('UserName', str(user))[0]["fields"]
        groups = record["ChatGroup"].split(',')
    return json.dumps(groups)


@app.route("/get_resources/")
def get_resources():
    url1 = "https://www.womenwhocode.com/digital"
    url2 = "https://ghc.anitab.org/attend/vghc-career-fair-extension/"
    url3 = "https://womeninstem.org/calendar?view=calendar"
    url4 = "https://www.womenintechnology.org/index.php?option=com_jevents&Itemid=116&task=."
    return {"Women Who Code": url1, "Anita borg": url2, "Women in STEM": url3, "Women in Tech": url4}


def upload_to_s3(filename):
    s3 = boto3.client('s3')
    s3.upload_file(filename, 'sigmoidhack', filename)


def make_attachment(url):
    return [{'url': url}]


@app.route("/post_profile/", methods=['POST'])
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
