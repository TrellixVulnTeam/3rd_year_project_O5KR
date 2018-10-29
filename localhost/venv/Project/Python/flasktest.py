import csv
import time
import datetime
import json
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('main.html')

def parseTableName(input):
    parsedInput = input.replace("-", "_")
    return parsedInput

#STOP CALL WHEN MATCH FINISHED
#RETURN SPECIFIC MESSAGE WHEN MATCH NOT STARTED YET
#ONLY ADD NEW COMMENTARY, NEED TO CHECK IF UPDATE IS NEW

@app.route("/teamSelected", methods=['POST', 'GET'])
def new():
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")

        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]
        tempTableName = homeTeam + awayTeam + splitData[2]
        tableName = parseTableName(tempTableName)
        #print("Dropping table " + tableName)




        cursor.execute("DROP TABLE if exists "+tableName)
        cursor.execute("DROP TABLE if exists " + tableName+"stats")
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tableName + "';")
        result = cursor.fetchone()
        number_of_rows = result[0]

        #cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tableName + "stats';")

        #print("RIGHT HERE " + str(number_of_rows))
        if(number_of_rows == 0):
            #CREATE TABLE
            create_table_string = "create table if not exists '"+ tableName + "' (id INTEGER PRIMARY KEY, commentary TEXT, time TEXT)"
            cursor.execute(create_table_string)

            create_table_string = "create table if not exists '" + tableName + "stats' (id INTEGER PRIMARY KEY, matchState TEXT, homeScore INTEGER, awayScore INTEGER, time TEXT, homePossession TEXT, awayPossession TEXT, homeGoalAttempts INTEGER, awayGoalAttempts INTEGER, homePasses INTEGER, awayPasses INTEGER)"
            cursor.execute(create_table_string)

            def scrapeInfo():
                URLID = 0

                homeTeamSearch = homeTeam.replace("-", " ")
                awayTeamSearch = awayTeam.replace("-", " ")

                now = datetime.datetime.now()
                year = now.year
                nextYear = year + 1




                with open('static/csv/gamesToday.csv') as file:
                    reader = csv.reader(file)
                    count = 0

                    for row in reader:
                        if count == 0:
                            count += 1
                            continue
                        if len(row) == 0:
                            continue
                        else:
                            if (row[1] == homeTeamSearch) & (row[2] == awayTeamSearch):
                                URLID = row[3]


                try:
                    #myurl = "https://www.scoreboard.com/uk/match/levante-alaves-2018-2019/GKbBmhbD/#live-commentary;0"
                    myurl = "https://www.scoreboard.com/uk/match/"+str(homeTeam)+"-"+str(awayTeam)+"-"+str(year)+"-"+str(nextYear)+"/"+str(URLID)+"/#live-commentary;0"
                    browser = webdriver.Chrome()
                    browser.get(myurl)

                    myurl2 = "https://www.scoreboard.com/uk/match/" + str(homeTeam) + "-" + str(awayTeam) + "-" + str(year) + "-" + str(nextYear) + "/" + str(URLID) + "/#match-summary|match-statistics;0|lineups;1"
                    browser2 = webdriver.Chrome()
                    browser2.get(myurl2)

                except:
                    print("Live commentary not available")

                pageLoad = False
                times = 0
                commentary = 0

                times = []
                commentaryUpdates = []
                awayTeams = []

                checkNumber = True

                def parseUpdate(input):
                    check = 0
                    if (input.strip() != ""):
                        input = input.replace("\n", '')
                    return input

                def isNumber(input):
                    parsed = input.strip()[:-1]
                    number = 0
                    try:
                        number = int(parsed)
                        return True
                    except:
                        pass

                    try:
                        if "+" in parsed:
                            splitResult = parsed.split("+")
                            for numResult in splitResult:
                                number += int(numResult)
                        else:
                            return false
                    except:
                        return False
                    return True
                matchAlive = True

                #print("before scrape")

                def scrapeData():
                    matchState = ""
                    homeScore = ""
                    awayScore = ""
                    matchTimeText = ""
                    homePossessionText = ""
                    awayPossessionText = ""
                    homeGoalAttemptText = ""
                    awayGoalAttemptText = ""
                    homePassText = ""
                    awayPassText = " "

                    pageLoad = False
                    checkNumber = True

                    while pageLoad != True:
                        print("in while")
                        updates = browser.find_elements_by_css_selector(".phrase.fl ")
                        matchTime = browser2.find_elements_by_class_name("mstat")
                        stats = browser2.find_elements_by_id("tab-statistics-0-statistic")
                        scoreboard = browser2.find_elements_by_class_name("scoreboard")

                        if len(scoreboard) == 0:
                            print("page not loaded yet!")
                            time.sleep(0.5)
                            continue

                        homeScore = scoreboard[0].text
                        awayScore = scoreboard[1].text
                        matchTimeText = matchTime[0].text

                        if (homeScore == "-") & (awayScore == "-"):
                            matchState = -1
                            print("MATCH NOT STARTED YET")
                            time.sleep(45)
                            continue
                        else:
                            if len(stats) == 0:
                                print("stats area not loaded yet!")
                                time.sleep(0.5)
                                continue
                            else:
                                matchState = 0
                                if matchTimeText.lower() == "finished":
                                    matchState = 1
                                oddRows = stats[0].find_elements_by_class_name("odd")
                                evenRows = stats[0].find_elements_by_class_name("even")

                                for row in oddRows + evenRows:
                                    if ("ball possession" in row.text.lower()):
                                        homePossessionElement = row.find_element_by_class_name("fl")
                                        awayPossessionElement = row.find_element_by_class_name("fr")
                                        homePossessionText = homePossessionElement.text
                                        awayPossessionText = awayPossessionElement.text
                                    elif ("goal attempts" in row.text.lower()):
                                        homeGoalAttemptElements = row.find_element_by_class_name("fl")
                                        awayGoalAttemptElements = row.find_element_by_class_name("fr")
                                        homeGoalAttemptText = homeGoalAttemptElements.text
                                        awayGoalAttemptText = awayGoalAttemptElements.text
                                    elif ("total passes" in row.text.lower()):
                                        homePassElements = row.find_element_by_class_name("fl")
                                        awayPassElements = row.find_element_by_class_name("fr")
                                        homePassText = homePassElements.text
                                        awayPassText = awayPassElements.text

                        if (len(updates) == 0):
                            #print("page not loaded yet!")
                            time.sleep(0.5)
                            continue

                        for commentaryResult in updates:
                            #print(commentaryResult.text)
                            value = parseUpdate(commentaryResult.text)
                            if ((checkNumber) & (isNumber(value))):
                                times.append(value)
                                checkNumber = False
                            elif not checkNumber:
                                commentaryUpdates.append(value)
                                checkNumber = True
                            else:
                                pass

                        pageLoad = True
                    maxUpdate = 5
                    updateNumber = 0

                    print("inserting to stats table..")
                    #matchState TEXT, homeScore INTEGER, awayScore INTEGER, time TEXT,
                    #homePossession TEXT, awayPossession TEXT, homeGoalAttempts INTEGER, awayGoalAttempts INTEGER, homePasses INTEGER, awayPasses INTEGER)


                    cursor.execute("INSERT INTO " + tableName + "stats (matchState, homeScore, awayScore, time, homePossession, awayPossession, homeGoalAttempts, awayGoalAttempts, homePasses, awayPasses) VALUES(?,?,?,?,?,?,?,?,?,?)", (matchState, homeScore, awayScore, matchTimeText, homePossessionText, awayPossessionText, homeGoalAttemptText, awayGoalAttemptText, homePassText, awayPassText))
                    print("I N S E R T E D")
                    #cursor.execute("select * from " + tableName+"stats")
                    #rows = cursor.fetchall()
                   # for row2 in rows:
                       # print(row2)

                    newCommentaryUpdates = []
                    newTimeUpdates = []
                    commentaryUpdatesLength = len(commentaryUpdates) - 1
                    matchNumber = 0
                    cursor.execute("select * from " + tableName + " order by id desc limit " + str(maxUpdate))
                    rows = cursor.fetchall()
                    if (len(rows) == 0):
                        arrayIndex = len(commentaryUpdates) -1
                        while(arrayIndex >= 0):
                            cursor.execute("INSERT INTO " + tableName + "(commentary, time) VALUES(?,?)",(commentaryUpdates[arrayIndex], times[arrayIndex]))
                            arrayIndex -= 1
                    else:
                        for row in rows:
                            print("HERE")
                            print(row[1] + "_______" + commentaryUpdates[matchNumber])
                            print("HERE")
                            if(commentaryUpdates[matchNumber] == row[1]):
                                break
                            else:
                                newCommentaryUpdates.prepend(commentaryUpdates[commentaryUpdatesLength - matchNumber])
                                newTimeUpdates.prepend(times[commentaryUpdatesLength - matchNumber])
                                matchNumber += 1

                        for commentEntry, timeEntry in zip(newCommentaryUpdates + newTimeUpdates):
                            cursor.execute("INSERT INTO " + tableName + "(commentary, time) VALUES(?,?)",(commentEntry, timeEntry))

                    print("printing...")
                    cursor.execute("select * from " + tableName)
                    rows = cursor.fetchall()
                    for row2 in rows:
                        print(row2)
                    print("printed...")

                    with open("static/csv/lastUpdate.csv", mode="w+") as file:
                        fileWriter = csv.writer(file)
                        fileWriter.writerow([times[0], commentaryUpdates[0]])
                    file.close()

                    commentaryUpdates.clear()
                    times.clear()
                    connection.commit()
                    #print("committed update")
                    #cursor.execute("select * from "+tableName)
                    rows = cursor.fetchall()

                    #for row in rows:
                        #print(row)
                    if(matchState == 1):
                        #browser.close()
                        #browser2.close()
                        print("Match finished so terminating script")
                        #return

                    time.sleep(20)
                    scrapeData()
                try:
                    print("now calling to scrape page")
                    scrapeData()
                except Exception as e:
                    print(e)
                    time.sleep(15)
                    scrapeData()
            try:
                print("calling scraping..")
                scrapeInfo()
            except Exception as e:
                print("error opening page - " + e)
                browser.close()
                time.sleep(15)
                scrapeInfo()
    except Exception as e:
        print(e)
        return jsonify("ERROR")

    return jsonify("CLEAN")

                #check if match finished
                #scrape
            #CREATE FUNCTION
                #scrape data
                #check if match finished
                    #if finished - terminate
                    #else continue
                #update table with updates


@app.route("/requestCommentary", methods=['POST', 'GET'])
def getCommentary():
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")

        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]
        tempTableName = homeTeam + awayTeam + splitData[2]
        tableName = parseTableName(tempTableName)
        maxUpdate = 5

        cursor.execute("select * from " + tableName + " order by id desc limit " + str(maxUpdate))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            commentaryUpdate = row[1]
            timeUpdate = row[2]
            result.append(timeUpdate + "___" + commentaryUpdate)
        return jsonify(result)

    except Exception as e:
        print(e)
        return jsonify("ERROR")


@app.route("/quickStats", methods=['POST', 'GET'])
def stats():
    print("Now in the stats section")
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")


        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]

        tempTableName = homeTeam + awayTeam + splitData[2] +"stats"
        tableName = parseTableName(tempTableName)


       # cursor.execute("SELECT * FROM " + tableName)
        #rows = cursor.fetchall()
        #for row in rows:
            #print(row)

        cursor.execute("SELECT * FROM " + tableName + " ORDER BY id DESC LIMIT 1")
        rows = cursor.fetchall()
        result = []


        for row in rows:
            matchState = row[1]
            homeScore = row[2]
            awayScore = row[3]
            matchTimeText =  row[4]
            homePossessionText = row[5]
            awayPossessionText = row[6]
            homeGoalAttemptText = row[7]
            awayGoalAttemptText = row[8]
            homePassText = row[9]
            awayPassText = row[10]

            result = {"matchState": matchState, "homeScore": homeScore, "awayScore": awayScore, "time": matchTimeText,
                    "homePossession": homePossessionText, "awayPossession": awayPossessionText,
                    "homeGoalAttempts": homeGoalAttemptText, "awayGoalAttempts": awayGoalAttemptText,
                    "homePasses": homePassText, "awayPasses": awayPassText}
        return jsonify(result)

    except Exception as e:
        print(e)
        print("H E R R O R")
        return jsonify("ERROR")

@app.route("/tinyDelayRequest", methods=['POST', 'GET'])
def tinyDelay():
    print("T I N Y  D E L A Y ")
    time.sleep(1)
    return jsonify("done")

@app.route("/delayRequest", methods=['POST', 'GET'])
def delay():
    time.sleep(10)
    return jsonify("done")

@app.route("/largeDelayRequest", methods=['POST', 'GET'])
def largeDelay():
    time.sleep(25)
    return jsonify("done")


if __name__ == "__main__":
    app.run(debug=True)

