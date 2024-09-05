from datetime import datetime

import icalendar
import requests
import yaml
import mysql.connector
import csv


def load_teams(config):
    with open('teams.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        mydb = get_mysql_connection(config)
        cursor = mydb.cursor()
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            #print(
            # f'\t{row["Name"]}.')

            sql = "INSERT INTO {0} (name, manager, team, role, product) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=%s,manager=%s,team=%s,role=%s, product=%s".format(
                config["teams"]["db_table"])
            val = (row["Name"], row["Manager"], row["Team"], row["Role"], row["Product"], row["Name"], row["Manager"],
                   row["Team"], row["Role"], row["Product"])

            cursor.execute(sql, val)

            line_count += 1
        mydb.commit()


def get_mysql_connection(config):
    mysql_host = config["mysql"]["host"]
    mysql_user = config["mysql"]["username"]
    mysql_password = config["mysql"]["password"]
    mysql_database = config["mysql"]["database"]

    mydb = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database)

    return mydb


def build_description(event):
    s = str(event.decoded("dtstart"))
    e = str(event.decoded("dtend"))
    dt_s = datetime.fromisoformat(s)
    dt_e = datetime.fromisoformat(e)
    description = "Unknown"

    if dt_s.strftime("%Y-%m-%d") == dt_e.strftime("%Y-%m-%d"):
        # Ok start and end date same day, so must be a half day holiday

        s_h = dt_s.strftime("%H")
        if int(s_h) < 12:
            description = "Half day AM"
        else:
            description = "Half day PM"
    else:
        description = "{0} day(s)".format((dt_e - dt_s).days)

    return description


def load_holidays(config, path_to_ics_file):
    with open(path_to_ics_file, 'wb') as out_file:
        content = requests.get(config["holidays"]["feed_url"], stream=True).content
        out_file.write(content)

    with open(path_to_ics_file) as f:
        calendar = icalendar.Calendar.from_ical(f.read())

        mydb = get_mysql_connection(config)

        cursor = mydb.cursor()

        for event in calendar.walk('VEVENT'):
            if str(event.get("SUMMARY")).lower().find("holiday") != -1:
                author = event.get("DESCRIPTION").lower()[12::]  # strip out "Created By :" from start of string
                name = str(event.get("SUMMARY").lower())[:-10]  # strip off "- holiday" at end of string
                print(event.get("dtstart"))

                description = build_description(event)

                sql = "INSERT INTO {0} (author, name, startDate, endDate, description) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE author=%s,name=%s,startDate=%s,endDate=%s,description=%s".format(
                    config["holidays"]["db_table"])
                val = (author, name, event.decoded("dtstart"), event.decoded("dtend"), description,
                       author, name, event.decoded("dtstart"), event.decoded("dtend"), description)

                cursor.execute(sql, val)

    mydb.commit()


if __name__ == "__main__":
    with open('config.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    load_teams(config)
    load_holidays(config, "holidays.ics")
