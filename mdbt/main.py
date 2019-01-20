#!/usr/bin/python
import os
import sqlite3


import subprocess
from optparse import OptionParser

global conn

def setup(dbname):
    global conn
    conn = sqlite3.connect(dbname)


def parse_args():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage, version="%prog 1.0.0")
    parser.add_option("--db", dest="db_name")
    parser.add_option("--prep-night", action="store", dest="prep_night")
    parser.add_option("--scrub",action="store_const", const="scrub", dest="action")

    (opts, args) = parser.parse_args()
    return opts, args


def main():
    (options, args) = parse_args()
    setup(options.db_name)

    if options.action == "scrub":
        scrub_db()

    if options.prep_night is not None:
        prep_night(options.prep_night)


def scrub_db():
    global conn

    scrub_count = 0
    for crate in list_of_crate_ids():
        crate_id=crate[0]
        crate_size = calculate_crate_size(crate_id)
        if crate_size < 2:
            print("Crate %s has %d tracks. Scrubbing" % (crate_id, crate_size))
            conn.execute('DELETE FROM crate_tracks WHERE crate_id = ?', (crate_id, ))
            conn.commit()
            conn.execute('DELETE FROM crates WHERE id = ?', (crate_id, ))
            scrub_count=scrub_count+1
            conn.commit()
    print("Removed %d crates." % (scrub_count))

    scrub_count = 0
    for playlist in list_of_playlist_ids():
        playlist_id=playlist[0]
        playlist_size = calculate_playlist_size(playlist_id)
        if playlist_size < 3:
            print("Playlist id %s has %d tracks. Scrubbing" % (playlist_id, playlist_size))
            conn.execute('DELETE FROM playlisttracks WHERE playlist_id = ?', (playlist_id, ))
            conn.commit()
            conn.execute('DELETE FROM playlists WHERE id = ?', (playlist_id, ))
            scrub_count = scrub_count+1
            conn.commit()
    print("Removed %d playlists." % (scrub_count))


def calculate_crate_size(crate):
    global conn

    values = (crate,)
    rows = conn.execute('SELECT COUNT(track_id) FROM crate_tracks WHERE crate_id = ?', values)
    for row in rows:
        return row[0]

def calculate_playlist_size(playlist):
    global conn

    values = (playlist,)
    rows = conn.execute('SELECT COUNT(track_id) FROM playlisttracks WHERE playlist_id = ?', values)
    for row in rows:
        return row[0]

def prep_night(night):
    global conn

    conn.execute("UPDATE crates SET name ='~~'||name WHERE name LIKE '!0%'")
    conn.commit()

    prefixes = {
        "!000 - %s",
        "!010 - %s",
        "!011 - %s",
        "!020 - %s",
        "!021 - %s",
        "!030 - %s",
        "!031 - %s"
    }

    for prefix in prefixes:
        create_crate(prefix % night)

    scramble_crate = '!001 - %s' % night
    create_crate(scramble_crate)

    crate_id = find_crate_by_name(scramble_crate)

    conn.execute("DROP TABLE IF EXISTS mdbt_temp")
    conn.commit()
    conn.execute("CREATE TABLE mdbt_temp (track_id INTEGER, last_played DATETIME, times_played INTEGER)")
    conn.commit()
    conn.execute("INSERT INTO mdbt_temp SELECT track_id, MAX(PlaylistTracks.pl_datetime_added) AS last_played, "
                 "count(track_id) AS times_played FROM PlaylistTracks GROUP BY track_id")
    conn.commit()
    conn.execute("INSERT INTO crate_tracks SELECT ?, track_id FROM mdbt_temp "
                 "WHERE mdbt_temp.last_played < date('now','-8 month') ORDER BY mdbt_temp.times_played DESC,"
                 "mdbt_temp.last_played LIMIT 100", (crate_id,))
    conn.commit()
    conn.execute("VACUUM")
    conn.commit()


def play_song(filename):
    proc = subprocess.Popen(
        ['mplayer', filename
         ])
    proc.wait()

def add_song_to_crate(song_id, crate_id):
    values = (crate_id, song_id,)
    try:
        conn.execute('INSERT INTO crate_tracks (crate_id, track_id) VALUES (?,?)', values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        print("Error adding track to crate - possibly already exists? %s" % e)
        raw_input("[Enter]")


def list_of_crate_ids():
    global conn
    return conn.execute('SELECT id FROM crates')


def list_of_playlist_ids():
    global conn
    return conn.execute('SELECT id FROM playlists')


def songs_to_process():
    global conn

    values = (find_crate_by_name('~Processed~'),)
    return conn.execute(
        'SELECT library.id,title,artist,bpm, track_locations.location FROM library,track_locations '
        'WHERE track_locations.id=library.id AND '
        'library.id NOT IN (SELECT track_id FROM crate_tracks WHERE crate_id=?) ORDER BY library.id',
        values)


def create_crate(name):
    global conn
    values = (name,)
    conn.execute('INSERT INTO crates (name) VALUES (?)', values)
    conn.commit()


def find_crate_by_name(name):
    global conn

    values = (name,)
    rows = conn.execute('SELECT id FROM crates WHERE name =?', values)
    for row in rows:
        return row[0]


if __name__ == "__main__":
    main()
