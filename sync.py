#!/usr/bin/env python
import click
import requests
from analysis import count_tags, filter_tags_by_date_range, parse_begin_end
from merge import extract_tags_from_file
import datetime as dt
import configparser
import os


class BeeminderGoal:
    def __init__(self, user, goal, auth_token, gap=0.75):
        self.user = user
        self.goal = goal
        self.auth_token = auth_token
        self.datapoints = self.get_datapoints()
        self.days = [d['daystamp'] for d in self.datapoints]
        self.gap = gap

    def get_datapoints(self, ):
        url = 'https://www.beeminder.com/api/v1/users/{}/goals/{}/datapoints.json?auth_token={}'.format(
            self.user, self.goal, self.auth_token)
        response = requests.get(url)
        return sorted(response.json(), key=lambda x: x['timestamp'])

    def post_datapoint(self, daystamp, value):
        if value == 0:
            return 0
        url = 'https://www.beeminder.com/api/v1/users/{}/goals/{}/datapoints.json'.format(
            self.user, self.goal)
        params = {
            'daystamp': daystamp,
            'value': value,
            'auth_token': self.auth_token
        }
        requests.post(url, data=params)
        print('synced {}'.format(daystamp))

    def delete_data_for_day(self, daystamp):
        for d in self.datapoints:
            if d['daystamp'] == daystamp:
                ID = d['id']
                url = 'https://www.beeminder.com/api/v1/users/{}/goals/{}/datapoints/{}.json?auth_token={}'.format(
                    self.user, self.goal, ID, self.auth_token)
                requests.delete(url)
        print('deleted data for {}'.format(daystamp))

    def isConsistent(self, daystamp, new_value):
        value = 0
        for d in self.datapoints:
            if d['daystamp'] == daystamp:
                value += d['value']
        return abs(value-new_value) < 10e-4


def get_daily_count(tags):
    begin_dt = dt.datetime.fromtimestamp(min(tags))
    begin_day = dt.date(
        year=begin_dt.year, month=begin_dt.month, day=begin_dt.day)
    end_day = dt.date.today()
    duration = end_day - begin_day
    days = [begin_day + dt.timedelta(d) for d in range(1, duration.days)]
    counts = {}
    for day in days:
        day_begin = dt.datetime.combine(day, dt.time())
        day_end = dt.datetime.combine(day + dt.timedelta(1), dt.time())
        f_tags = filter_tags_by_date_range(tags, day_begin, day_end)
        counts[day_begin.strftime('%Y%m%d')] = count_tags(f_tags)
    return counts


def sumTagTime(count, synctags, gap):
    value = 0
    for tag in synctags:
        value += count.get(tag, 0) * gap
    return value


def parse_config(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    return config


@click.command()
@click.argument(
    'path', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('goal')
@click.option(
    '-c',
    '--config',
    'configfile',
    help='path to config',
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=os.path.expanduser('~/.bmndrrc'))
@click.option(
    '--tags', 'synctags', default='', help='comma seperated list of tags')
@click.option(
    '--gap', 'gap', default=0.75, help='average interval between tags')
@click.option(
    '--update',
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
