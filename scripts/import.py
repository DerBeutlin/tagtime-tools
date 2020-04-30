#!/usr/bin/env python
import sqlite3
import click
from tagtime.merge import write_tag_dict_to_file, print_tag_dict


@click.command()
@click.argument('database',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-o',
              '--output',
              'output_file',
              type=click.Path(writable=True, resolve_path=True),
              default=None,
              help='output file')
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

    if output_file:
        write_tag_dict_to_file(output_file, tags_at_ping)
    else:
        print_tag_dict(tags_at_ping)


if __name__ == '__main__':
    import_tags_from_database()
