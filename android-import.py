#!/usr/bin/env python

import sqlite3
import click


@click.command()
@click.argument('database', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('output_file', type=click.Path(writable=True, resolve_path=True))
def import_tags_from_database(database, output_file):
    '''import database and write the tags to the output file as a normal tagtime log'''
    conn = sqlite3.connect(database)
    c = conn.cursor()

    c.execute('SELECT _id ,ping  from pings')
    pings = dict(c.fetchall())

    c.execute('SELECT _id, tag from tags')
    tags = dict(c.fetchall())

    c.execute('SELECT _id ,ping_id, tag_id from tag_ping')
    ping_tags = c.fetchall()

    tags_at_ping = {}
    for _, ping_id, tag_id in ping_tags:
        if pings[ping_id] not in tags_at_ping.keys():
            tags_at_ping[pings[ping_id]] = []
        tags_at_ping[pings[ping_id]].append(tags[tag_id])

    with open(output_file,'w') as f:
        for time in sorted(tags_at_ping.keys()):
            string = str(time) + ' ' + ' '.join(tags_at_ping[time]) + '\n'
            f.write(string)


if __name__ == '__main__':
    import_tags_from_database()
