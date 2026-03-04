---
title: "Temporary Postgres Databases"
date: 2026-03-03
categories: ['postgres']
type: post
---

When teaching my undergraduate database course, I often have the need for writing little "throwaway" SQL tables and queries to help illustrate concepts or to test out a feature. Connecting to the "real" course server
is inconvenient for a number of reasons: there is too much friction with my password manager to get the right login for the database, I have to make sure I'm on the right WiFi network (thanks to new IT policies), and I'd like to be able to demonstrate queries/actions that may cause problems for the course server without worrying about breaking anything.

Running your own postgres instance locally can also be a pain: remembering all the right `docker` flags to provide, cleaning up old state after you're done, etc. Then there's the trouble of having to write out the `psql` command for connecting to the database.
Could I just put all this in a couple of scripts? Yes! And that's what I did. But I still felt that I wasn't able to quickly do everything that I wanted.

Enter `pg`. It's about 300 lines of Python that provides some convenience around postgres Docker containers.

```bash
pg -h
usage: pg [-h] [-c COMMAND] [-s SCHEMA] [-d DATABASE] [--dir DIR] [--rc FILE] [--default-rc] [--image IMAGE]
          [--pg VERSION] [--nuke] [--stream-logs] [--conn-string]
          [file.sql ...]

Spin up a temporary PostgreSQL database and drop into psql.

positional arguments:
  file.sql              SQL files to run before the interactive session

options:
  -h, --help            show this help message and exit
  -c, --command COMMAND
                        Run a SQL command and exit
  -s, --schema SCHEMA   Create and use this schema
  -d, --database DATABASE
                        Database name (default: postgres)
  --dir DIR             Host directory to bind-mount for persistent data
  --rc FILE             psqlrc file to load on startup (in addition to built-in defaults)
  --default-rc          Use default psql behavior (skip built-in psqlrc)
  --image IMAGE         Docker image to use (e.g. postgis/postgis:16-3.4)
  --pg VERSION          PostgreSQL version (e.g. 16, 15.3)
  --nuke                Stop and replace any running temppg container before continuing
  --stream-logs         Stream Docker container logs while pg is running
  --conn-string         Print the connection string for the selected database and exit
```

Here are the main features:

I can create a database as easily as:

```bash
pg
```

This creates the database and immediately drops me into the psql prompt.
If I want to customize the image or postgres version, I can do that with flags:

```bash
# for postgies
pg --image postgis/postgis:16-3.4
# for timescaledb
pg --image timescale/timescaledb:latest-pg16
# for vanilla postgres in an older version
pg --version 15
```

I can quickly load in SQL files that build tables or run example queries:

```bash
pg schema.sql queries.sql
```

This just runs `\i` on each file, in order.

A key feature of `pg` is if I run it multiple times, I will get new `psql` sessions into the same database. This is really helpful for demos where I want to illustrate multiple sessions interacting with the same database state.

I've been using this script for a few months and I use it almost every class session.
I added a couple features recently: `--nuke` to stop and replace any existing `temppg` container, and `--stream-logs` to stream the Docker container logs while `pg` is running.
I can also use `pg --conn-string` to print out the connection string for the database and then connect with any client I want.

Available for download at [pg](https://git.sr.ht/~gabe/pg). I clone it locally
and then install with `uv tool install -e .` from within the directory.
I'm not planning to push it to any package repository because I don't want to compromise on the name of the package :).
