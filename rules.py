#!/usr/bin/env python
import csv
import click
from merge import extract_tags_from_file, print_tag_dict, write_tag_dict_to_file
from warnings import warn


class Rule(object):
    def __init__(self, triggers, actions):
        self.triggers = triggers
        self.actions = actions

    def check(self, input_tags):
        return self.logicOperator([t in input_tags for t in self.triggers])

    def apply(self, input_tags):
        if self.check(input_tags):
            return self.actions
        return []


class AndRule(Rule):
    def __init__(self, triggers, actions):
        super().__init__(triggers, actions)
        self.logicOperator = all


class OrRule(Rule):
    def __init__(self, triggers, actions):
        super().__init__(triggers, actions)
        self.logicOperator = any


def parse_rules(rule_file):
    with open(rule_file) as f:
        reader = csv.reader(f, delimiter='~')
        rules = []
        triggers, actions = list(zip(*reader))
        for trig, act in zip(triggers, actions):
            if '|' in trig and '&' in trig:
                warn('mixing | and & in trigger list is not allowed, skipping')
                continue
            elif '&' in trig:
                rules.append(AndRule([t.strip() for t in trig.split('&')], [
                             a.strip() for a in act.split(',')]))
            else:
                rules.append(OrRule([t.strip() for t in trig.split('|')], [
                             a.strip() for a in act.split(',')]))
    return rules


@click.command()
@click.argument('tag_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('rule_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-o', '--output', 'output_path', type=click.Path(writable=True, resolve_path=True), help='output file', default=None)
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
