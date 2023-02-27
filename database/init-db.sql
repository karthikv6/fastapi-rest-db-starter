create database if not exists ece140;

use ece140;

-- DUMP EVERYTHING... YOU REALLY SHOULDN'T DO THIS!
drop table if exists users;

-- 1. Create the users table
create table if not exists users (
  id int primary key auto_increment,
  first_name varchar(255) not null,
  last_name varchar(255) not null
);


-- 2. Insert initial seed records into the table
insert into users (first_name, last_name) values
  ('John', 'Doe'),
  ('Jane', 'Doe');
