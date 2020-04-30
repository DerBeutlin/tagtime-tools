#!/usr/bin/env python3
import matplotlib.pyplot as plt
from tagtime.analysis import parse_begin_end,filter_tags_by_date_range,get_hours_per_period_with_error,count_tags
from tagtime.merge import extract_tags_from_file
import click
import numpy as np
@click.command()
@click.argument(
    'path', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('controlled_vocabulary_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-b', '--begin', 'begin', help='begin date', default=None)
@click.option('-e', '--end', 'end', help='end date', default=None)
@click.option(
    '-g', '--gap', 'gap', help='TagTime interval in hours', default=0.75)
@click.option('-p', '--period', 'period', help='period in hours', default=24)
@click.option(
    '-o',
    '--output-file',
    'output_file',
    type=click.Path(writable=True, resolve_path=True),
    help='output file',
    default=None)
def plot_estimations(path, controlled_vocabulary_file,begin, end, gap, period, output_file):
    '''print estimations with higher and lower bound in table'''
    import matplotlib
    matplotlib.use('WebAgg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 5})
    controlled_vocabulary = []
    with open(controlled_vocabulary_file) as f:
        for line in f.readlines():
            controlled_vocabulary.append(line.split())
    relevant_tags = controlled_vocabulary[0]
    begin, end = parse_begin_end(begin, end)
    tags = extract_tags_from_file(path)
    tags = filter_tags_by_date_range(tags, begin, end)
    counts = count_tags(tags)
    stats = get_hours_per_period_with_error(counts, gap, period)
    stats = {k:v for k,v in stats.items() if k in relevant_tags and v['mean']>=0.01}
    stats = dict(sorted(stats.items(), key=lambda item: item[1]['mean'],reverse=True))
    fig, ax = plt.subplots(figsize=(1920/300, 1080/300), dpi=300)
    sizes = [s['mean'] for s in stats.values()]
    labels = list(stats.keys())
    def func(pct, allvals):
        absolute = pct/100.*np.sum(allvals)
        return "({0:.2f} h)".format(absolute)
    ax.pie(sizes,labels=labels,autopct=lambda pct: func(pct, sizes),labeldistance=1.3)
    fig.suptitle('Stunden pro Tag ausgewertet über eine Woche')
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()


if __name__ == '__main__':
    plot_estimations()
