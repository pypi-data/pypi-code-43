#!/usr/bin/env python3

import logging
import sqlite3

create_leaderboards = """
CREATE TABLE IF NOT EXISTS leaderboards (
event_id TEXT PRIMARY KEY,
name TEXT,
url TEXT,
take INTEGER);
"""
insert_leaderboard = "INSERT OR REPLACE INTO leaderboards VALUES (?,?,?,?);"
select_leaderboard = "SELECT * FROM leaderboards WHERE event_id == ?"

create_teams = """
CREATE TABLE IF NOT EXISTS teams (
team_id TEXT PRIMARY KEY,
name TEXT,
rank INTEGER,
score INTEGER,
solves INTEGER,
start TEXT,
event_id TEXT);
"""
insert_team = "INSERT OR REPLACE INTO teams VALUES (?,?,?,?,?,?,?);"
select_team = "SELECT * FROM teams WHERE team_id == ?"
all_teams_for_event_by_rank = "SELECT * FROM teams WHERE event_id == ? ORDER BY rank"
all_teams_for_event_by_id = "SELECT * FROM teams WHERE event_id == ? ORDER BY team_id"

create_solves = """
CREATE TABLE IF NOT EXISTS solves (
team_id TEXT,
points INTEGER,
chals INTEGER,
time timestamp);
"""

insert_solve= "INSERT INTO solves VALUES (?,?,?,?);"

tables = [create_leaderboards, create_teams, create_solves]

# global connection, loaded during initialization
conn = None

def load(path):
    logging.debug("Loading database: {}".format(path))
    global conn
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for table in tables:
        c.execute(table)
    conn.commit()

def store_event(event_id, name, url, take):
    c = conn.cursor()
    c.execute(insert_leaderboard, (event_id, name, url, take))
    conn.commit()

def event_by_id(event_id):
    c = conn.cursor()
    c.execute(select_leaderboard, (event_id,))
    return c.fetchone()

def all_events():
    c = conn.cursor()
    c.execute("SELECT * from leaderboards")
    return c.fetchall()

def store_team(team_id, name, rank, score, solves, start, event_id):
    c = conn.cursor()
    c.execute(insert_team, (team_id, name, rank, score, solves, start, event_id))
    conn.commit()

def store_all_teams(teams):
    c = conn.cursor()
    c.executemany(insert_team, teams)
    conn.commit()

def team_by_id(team_id):
    c = conn.cursor()
    c.execute(select_team, (team_id,))
    return c.fetchone()

def all_teams_by_rank(event_id):
    c = conn.cursor()
    c.execute(all_teams_for_event_by_rank, (event_id,))
    return c.fetchall()

def all_teams_by_id(event_id):
    c = conn.cursor()
    c.execute(all_teams_for_event_by_id, (event_id,))
    return c.fetchall()

def store_solve(team_id, points, chals, time):
    c = conn.cursor()
    c.execute(insert_solve, (team_id, points, chals, time))
    conn.commit()

def store_all_solves(solves):
    c = conn.cursor()
    c.executemany(insert_solve, solves)
    conn.commit()

