/* create database steam_clone; */


drop table if exists users cascade;
drop table if exists games cascade;
drop table if exists user_games cascade ;
drop table if exists user_games_data cascade ;
drop table if exists transactions cascade;

create table users(
user_id int primary key,
name varchar(50),
password varchar(255),
email varchar(100) check (email like '%@%'),
balance numeric(10,2) default 0.00
					 check (balance >= 0)
);

create table games(
game_id int primary key,
game_name varchar(100),
game_description varchar(255),
release_date date default current_date,
price numeric(10,2)
);

create table user_games(
user_games_id int primary key,
user_id int references users(user_id),
game_id int references games(game_id)
);

create table user_games_data(
user_games_id int references user_games(user_games_id),
time_played int default 0, /* time played in minutes */
date_purchase date default current_date 
);


create table transactions(
transaction_id int primary key,
user_id int references users(user_id),
amount numeric(10,2) check (amount > 0),
card_details varchar(200)
);


