#!/usr/bin/env python
import csv
import click
from merge import extract_tags_from_file, print_tag_dict, write_tag_dict_to_file


def parse_rules(rule_file):
    with open(rule_file) as f:
        reader = csv.reader(f, delimiter='~')
        trigger, action = list(zip(*reader))
        trigger = [[x.strip() for x in t.split(',')] for t in trigger]
        action = [[x.strip() for x in a.split(',')] for a in action]
        rules = trigger, action
    return rules


@click.command()
@click.argument('tag_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('rule_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-o', '--output', 'output_path', type=click.Path(writable=True, resolve_path=True), help='output file', default=None)
def apply_rules(tag_file, rule_file, output_path):
    trigger, action = parse_rules(rule_file)
    tag_dict = extract_tags_from_file(tag_file)
    for timestamp, tags in tag_dict.items():
        for i, t in enumerate(trigger):
            if tags.isdisjoint(t):
                continue
            for a in action[i]:
                tag_dict[timestamp].add(a)
    if output_path:
        write_tag_dict_to_file(output_path, tag_dict)
    else:
        print_tag_dict(tag_dict)


if __name__ == '__main__':
    apply_rules()
