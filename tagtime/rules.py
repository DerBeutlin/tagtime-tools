import csv
from warnings import warn


def check_tag(tag, input_tags):
    if tag.startswith('!'):
        return tag[1:].strip() not in input_tags
    return tag in input_tags


class Rule(object):
    def __init__(self, triggers, actions):
        self.triggers = triggers
        self.actions = actions

    def check(self, input_tags):
        if not input_tags:
            return False
        return self.logicOperator(
            [check_tag(t, input_tags) for t in self.triggers])

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
                rules.append(
                    AndRule([t.strip() for t in trig.split('&')],
                            [a.strip() for a in act.split(',')]))
            else:
                rules.append(
                    OrRule([t.strip() for t in trig.split('|')],
                           [a.strip() for a in act.split(',')]))
    return rules
