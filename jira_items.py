from jira import JIRA
import yaml
import mysql.connector

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

def loadItems(config):
    user = config["jira"]["user"]
    token = config["jira"]["token"]
    serverURL = config["jira"]["server_url"]

    jira = JIRA(basic_auth=(user, token), server=serverURL)

    position = 0
    numToFetch = 100


    mydb = get_mysql_connection(config)

    cursor = mydb.cursor()
    done = False
    while done != True:
        issues = jira.search_issues("project=preservica and fixversion=7.5.0 and type in(epic,bug)", startAt=position,
                                    maxResults=numToFetch)
        numResults = len( issues )
        position = position + numResults
        done = ( position >= issues.total )
        for issue in issues:
            print("Issue=", issue.key)
            print("Type=", issue.get_field("issuetype"))
            print("Summary=", issue.get_field("summary"))
            print("Fixversions=", issue.get_field("fixVersions"))
            print("Status=", issue.get_field("status"))

            fix_versions = None
            for fixversion in issue.get_field("fixVersions"):
                if fix_versions == None:
                    fix_versions = str(fixversion.name)
                else:
                    fix_versions = fix_versions + "," + str(fixversion.name)

            sql = "INSERT INTO {0} (issueKey, issuetype, summary, fixversion, status) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE  issuetype=%s,summary=%s,fixversion=%s,status=%s".format(config["jira"]["db_table"])

            print(sql)

            val = (issue.key, str(issue.get_field("issuetype")), issue.get_field("summary"), fix_versions, str(issue.get_field("status")),  str(issue.get_field("issuetype")), issue.get_field("summary"), fix_versions, str(issue.get_field("status")))


            print(val)
            cursor.execute(sql, val)

    mydb.commit()


if __name__ == "__main__":
    with open('config.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    loadItems(config)
