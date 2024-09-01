use dashboard;
drop table b1;

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