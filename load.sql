use dashboard;
drop table b1;
drop table jira;

CREATE TABLE IF NOT EXISTS b1(
	id int,
	number int,
	startDate DATETIME,
	parentBuildTypeId varchar(100),
    buildTypeId varchar(100),
	branch varchar(100),
	status varchar(20),
	PRIMARY KEY(id)
);



CREATE TABLE IF NOT EXISTS jira(
	issueKey varchar(50),
	issuetype varchar(200),
	summary varchar(20),
	status varchar(20),
	fixversion varchar(50),
	PRIMARY KEY(issueKey)
);