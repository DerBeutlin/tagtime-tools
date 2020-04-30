#!/usr/bin/env python
import click
import tabulate
from tagtime.merge import extract_tags_from_file
from tagtime.analysis import get_hours_per_period_with_error, filter_tags_by_date_range, count_tags, parse_begin_end


@click.command()
@click.argument('path',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-b', '--begin', 'begin', help='begin date', default=None)
@click.option('-e', '--end', 'end', help='end date', default=None)
@click.option('-g',
              '--gap',
              'gap',
              help='TagTime interval in hours',
              default=0.75)
@click.option('-p', '--period', 'period', help='period in hours', default=24)
@click.option('--tbl-format',
              'tbl_format',
              help='table format from tabulate',
              default='simple')
@click.option('-o',
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
    table = tabulate(table,
                     headers=[
                         'Tag', 'h per {} h (mean)'.format(period),
                         'lower bound', 'upper bound'
                     ],
                     tablefmt=tbl_format)
    if not output_file:
        print(table)
    else:
        with open(output_file, 'w') as f:
            print(table, file=f)


if __name__ == '__main__':
    print_estimations()
