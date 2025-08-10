CREATE DATABASE IF NOT EXISTS employees;
USE employees;

CREATE TABLE IF NOT EXISTS employee (
    emp_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    primary_skill VARCHAR(100),
    location VARCHAR(100)
);

INSERT INTO employee VALUES 
('1','Amanda','Williams','Smile','local'),
('2','Alan','Williams','Empathy','alien'),
('3','Sandeep','Williams','Hello','alien'),
('4','Sandeep','Subedi','Hello','Pokhara'),
('5','Hem','Bhusal','chef','toronto'),
('6','Sam','Sam','cook','toronto');


