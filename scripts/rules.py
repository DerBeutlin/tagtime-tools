#!/usr/bin/env python
import click
from tagtime.merge import extract_tags_from_file, print_tag_dict, write_tag_dict_to_file
from tagtime.rules import parse_rules


@click.command()
@click.argument('tag_file',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('rule_file',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-o',
              '--output',
              'output_path',
              type=click.Path(writable=True, resolve_path=True),
              help='output file',
              default=None)
def apply_rules(tag_file, rule_file, output_path):
    '''apply rules to tags'''
    rules = parse_rules(rule_file)
    tag_dict = extract_tags_from_file(tag_file)
    for timestamp, tags in tag_dict.items():
        for rule in rules:
            for a in rule.apply(tags):
                tag_dict[timestamp].add(a)

    if output_path:
        write_tag_dict_to_file(output_path, tag_dict)
    else:
        print_tag_dict(tag_dict)


if __name__ == '__main__':
    apply_rules()
