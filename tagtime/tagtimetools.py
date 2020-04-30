#!/usr/bin/env python
import click
from merge import merge_tags
from androidimport import import_tags_from_database
from check import check_tags
from rules import apply_rules
from analysis import print_estimations
from sync import sync
@click.group()
def main():
    pass

main.add_command(merge_tags,name='merge')
main.add_command(import_tags_from_database,name='dbimport')
main.add_command(check_tags,name='check')
main.add_command(apply_rules,name='rules')
main.add_command(print_estimations,name='analysis')
main.add_command(sync,name='sync')

if __name__ == '__main__':
    main()
