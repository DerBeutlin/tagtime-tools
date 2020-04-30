import datetime as dt
import itertools
from collections import Counter
from dateutil.parser import parse as dparse

from collections import Counter, OrderedDict


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
