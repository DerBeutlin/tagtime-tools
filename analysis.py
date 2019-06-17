#!/usr/bin/env python
import click
from merge import extract_tags_from_file
import datetime as dt
from dateutil.relativedelta import relativedelta
import itertools
from collections import Counter, OrderedDict
from dateutil.parser import parse as dparse


def filter_tags_by_date_range(tags, begin_dt, end_dt):
    '''return the parts from tag dictionary which is within time range'''
    return {
        k: v
        for (k, v) in tags.items()
        if ((dt.datetime.fromtimestamp(k) > begin_dt) and (
            dt.datetime.fromtimestamp(k) < end_dt))
    }


def count_tags(tags):
    '''count the number of occurences of each tag and order the dictionary an additional tag called ALL is added'''
    tags_chained = list(itertools.chain.from_iterable(tags.values()))
    counts = Counter(tags_chained)
    counts['ALL'] = len(tags)
    return {
        k: counts[k]
        for k in sorted(counts, key=lambda x: counts[x], reverse=True)
    }


def get_bound(count, q):
    '''get upper/lower bound from gamma distribution'''
    from scipy.stats import gamma
    return gamma.ppf(q=q, a=count)


def parse_begin_end(begin, end):
    if not begin:
        begin = dt.datetime(1, 1, 1)
    else:
        begin = dparse(begin)
    if not end:
        end = dt.datetime.now()
    else:
        end = dparse(end)
    return begin, end


def get_hours_per_period_with_error(counts, gap, period):
    total_time = counts['ALL'] * gap
    number_of_periods = total_time / period
    stats = {}
    for tag, count in counts.items():
        stats[tag] = {
            'mean': count * gap / number_of_periods,
            'lower': get_bound(count, 0.05) * gap / number_of_periods,
            'upper': get_bound(count, 0.95) * gap / number_of_periods
        }
    return stats


@click.command()
@click.argument(
    'path', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-b', '--begin', 'begin', help='begin date', default=None)
@click.option('-e', '--end', 'end', help='end date', default=None)
@click.option(
    '-g', '--gap', 'gap', help='TagTime interval in hours', default=0.75)
@click.option('-p', '--period', 'period', help='period in hours', default=24)
@click.option(
    '--tbl-format',
    'tbl_format',
    help='table format from tabulate',
    default='simple')
@click.option(
    '-o',
    '--output-file',
    'output_file',
    type=click.Path(writable=True, resolve_path=True),
    help='output file',
    default=None)
def print_estimations(path, begin, end, gap, period, tbl_format, output_file):
    '''print estimations with higher and lower bound in table'''
    from tabulate import tabulate
    begin, end = parse_begin_end(begin, end)
    tags = extract_tags_from_file(path)
    tags = filter_tags_by_date_range(tags, begin, end)
    counts = count_tags(tags)
    stats = get_hours_per_period_with_error(counts, gap, period)
    table = []
    for tag, stat in stats.items():
        table.append([
            tag,
            round(stat['mean'], 2),
            round(stat['lower'], 2),
            round(stat['upper'], 2)
        ])
    table = tabulate(
        table,
        headers=[
            'Tag', 'h per {} h (mean)'.format(period), 'lower bound',
            'upper bound'
        ],
        tablefmt=tbl_format)
    if not output_file:
        print(table)
    else:
        with open(output_file, 'w') as f:
            print(table, file=f)


if __name__ == '__main__':
    print_estimations()
