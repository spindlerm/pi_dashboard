use dashboard;
drop table b1;
drop table jira;

CREATE TABLE IF NOT EXISTS b1 (
	id int,
	number int,
	startDate DATETIME,
	parentBuildTypeId varchar(100),
    buildTypeId varchar(100),
	branch varchar(100),
	status varchar(20),
	PRIMARY KEY(id)
) DEFAULT  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



CREATE TABLE IF NOT EXISTS jira  (
	issueKey varchar(50),
	issuetype varchar(200),
	summary varchar(200),
	status varchar(20),
	fixversion varchar(50),
	PRIMARY KEY(issueKey)
) DEFAULT  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;