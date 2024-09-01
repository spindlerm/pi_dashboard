import requests
import time
import mysql.connector
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XML, fromstring
import yaml


def retryable_request(url):
    HEADERS = {
        'Content-Type': 'application/json',
    }

    username = config["team_city"]["username"]
    tcPwd = config["team_city"]["password"]

    tries = 0
    max_retries = 10
    results_xml = None
    while tries < max_retries:
        try:
            request_results = requests.get(headers=HEADERS, url=url, cert='./x.pem', auth=(username, tcPwd), timeout=10)
            results_xml = fromstring(request_results.text)
            tries = 0
            break
        except:
            tries = tries + 1
            print("pb Exception Error, Retry, {0}".format(tries))
            if tries == max_retries:
                quit()
            time.sleep(10)

    return results_xml


def find_last_n_builds_of_type(config, build_Type, last_n):
    url_template = config["team_city"]["url_prefix"] + "/builds?locator=buildType:{0},branch:default:any&fields=build(id)".format(build_Type)
    url = url_template.format(build_Type)
    builds_xml = retryable_request(url)

    results = set()
    count = 0
    for build in builds_xml:
        if count >= last_n:
            break
        count = count + 1
        results.add(build.get("id"))

    return results


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


def process_snapshot_dependencies(config, build_xml):
    snapshot_dependencies = build_xml.findall("snapshot-dependencies/build")
    start_date = datetime.fromisoformat(build_xml.find("startDate").text).strftime("%Y-%m-%d %H:%M:%S")

    mydb = get_mysql_connection(config)

    cursor = mydb.cursor()
    for build in snapshot_dependencies:
        sql = "INSERT IGNORE INTO b1 (id, number, startdate, parentBuildTypeId, buildTypeId, branch, status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (build.get("id"), build.get("number"), start_date, build_xml.get("buildTypeId"), build.get("buildTypeId"),
               build.get("branchName"), build.get("status"))
        cursor.execute(sql, val)
    mydb.commit()


def process_build(config, build_id):
    url = config["team_city"]["url_prefix"] + "/builds/id:{0}".format(build_id)

    build_xml = retryable_request(url)

    process_snapshot_dependencies(config, build_xml)


def process_last_n_builds_of_type(config, build_type, last_n):
    print("Processing build:{0}".format(build_type))
    last_n_builds = find_last_n_builds_of_type(config, build_type, last_n)
    for build in last_n_builds:
        process_build(config, build)


if __name__ == "__main__":
    with open('config.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    build_types = ["PreservicaV6_2_Develop_DatabaseTests_AllDatabaseTests",
                   "PreservicaV6_2_Master_UnitTests_AllWebApps",
                   "PreservicaV6_2_Develop_IntegrationTests_2_AllIntegrationTests"]
    for build_type in build_types:
        process_last_n_builds_of_type(config, build_type, config["builds"]["lastn"])
