#!/usr/bin/env python
import click
import os
from tagtime.analysis import filter_tags_by_date_range, parse_begin_end
from tagtime.merge import extract_tags_from_file
from tagtime.sync import BeeminderGoal, get_daily_count, parse_config, sumTagTime


@click.command()
@click.argument('path',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('goal')
@click.option('-c',
              '--config',
              'configfile',
              help='path to config',
              type=click.Path(exists=True, readable=True, resolve_path=True),
              default=os.path.expanduser('~/.bmndrrc'))
@click.option('--tags',
              'synctags',
              default='',
              help='comma seperated list of tags')
@click.option('--gap',
              'gap',
              default=0.75,
              help='average interval between tags')
@click.option('--update',
              'update',
              is_flag=True,
              help='if set update existing datapoints')
@click.option('-b', '--begin', 'begin', help='begin date', default=None)
@click.option('-e', '--end', 'end', help='end date', default=None)
def sync(path, goal, synctags, gap, update, configfile, begin, end):
    '''sync tags in to beeminder goal'''
    begin, end = parse_begin_end(begin, end)
    synctags = set(synctags.split(','))
    tags = extract_tags_from_file(path)
    tags = filter_tags_by_date_range(tags, begin, end)
    counts = get_daily_count(tags)
    config = parse_config(configfile)
    user = config['account']['user']
    auth_token = config['account']['auth_token']
    bgoal = BeeminderGoal(user, goal, auth_token, gap)
    for day, count in counts.items():
        value = sumTagTime(count, synctags, gap)
        if day in bgoal.days:
            if (not update or bgoal.isConsistent(day, value)):
                continue
            else:
                bgoal.delete_data_for_day(day)
        bgoal.post_datapoint(day, value)


if __name__ == '__main__':
    sync()
