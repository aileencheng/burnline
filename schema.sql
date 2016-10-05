drop table if exists tasks;
drop table if exists users;
CREATE TABLE users (
    username TEXT PRIMARY KEY, 
    password TEXT NOT NULL,  
    start_time DATETIME NOT NULL, 
    end_time DATETIME NOT NULL
);
CREATE TABLE tasks (
    id integer primary key AUTOINCREMENT, 
    username TEXT NOT NULL, 
    title TEXT NOT NULL, 
    'description' TEXT, 
    weight INTEGER NOT NULL, 
    complete INTEGER NOT NULL, 
    FOREIGN KEY (username) REFERENCES users(username)
);