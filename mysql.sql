CREATE DATABASE IF NOT EXISTS employees;
USE employees;

CREATE TABLE IF NOT EXISTS employee(
emp_id VARCHAR(20),
first_name VARCHAR(20),
last_name VARCHAR(20),
primary_skill VARCHAR(20),
location VARCHAR(20));

INSERT INTO employee VALUES ('1','Amanda','Williams','Smile','local');
INSERT INTO employee VALUES ('2','Alan','Williams','Empathy','alien');
INSERT INTO employee VALUES ('3','Sandeep','Williams','Hello','alien');
INSERT INTO employee VALUES ('4','Sandeep','Subedi','Hello','Pokhara');
INSERT INTO employee VALUES ('5','Hem','Bhusal','chef','toronto');
INSERT INTO employee VALUES ('6','Sam','Sam','cook','toronto');


