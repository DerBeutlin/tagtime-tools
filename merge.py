#!/usr/bin/env python
import datetime as dt
import re
import copy
import click


def extract_tags_from_line(line):
    '''extracts tags and timestamp from line'''
    stamp, tags = line.split(' ', maxsplit=1)
    stamp = int(stamp)
    tags = re.sub(r'\[.*?\]', '', tags)
    tags = tags.split(' ')
    tags = list(filter(None, tags))
    tags = [tag.strip() for tag in tags]
    tags = set(filter(None, tags))
    return stamp, tags


def extract_tags_from_file(path):
    '''create a dictionary with timestmaps as key and tags as values'''
    tag_dict = {}
    with open(path, 'r') as f:
        for line in f.readlines():
            if not line.strip() or 'missed' in line:
                continue
            timestamp, tags = extract_tags_from_line(line)
            tag_dict[timestamp] = tags
    return tag_dict


def create_tag_string(timestamp, tags):
    stamp_string = str(timestamp)
    tag_string = ''
    for tag in tags:
        tag_string += tag.strip() + ' '
    time = dt.datetime.fromtimestamp(timestamp)
    time_string = time.strftime('\t[%Y.%m.%d %H:%M:%S %a]')
    return stamp_string + ' ' + tag_string + time_string


def write_tag_dict_to_file(path, tags_at_pings):
    '''write tags and timestamp to file'''
    with open(path, 'w') as f:
        for timestamp in sorted(tags_at_pings.keys()):
            f.write(create_tag_string(
                timestamp, tags_at_pings[timestamp])+'\n')


def print_tag_dict(tags_at_pings):
    '''print tags and timestamp'''
    for timestamp in sorted(tags_at_pings.keys()):
        print(create_tag_string(timestamp, tags_at_pings[timestamp]))


def remove_global_tags_not_present_in_both_sets(set1, set2, global_tags):
    '''for tags which have to be in both sets in order to be relevant e.g. like afk they are removed if not in both sets'''
    for global_tag in global_tags:
        if global_tag in set1 and off_tag not in set2:
            set1.remove(global_tag)
        elif global_tag not in set1 and global_tag in set2:
            set2.remove(global_tag)
    return set1, set2


def merge_tag_dicts(dict1, dict2, global_tags=[]):
    '''merge the tags from dict1 and dict2'''
    merged_dict = copy.deepcopy(dict1)
    for timestamp, tags in dict2.items():
        if timestamp not in merged_dict.keys():
            merged_dict[timestamp] = set([])
        merged_dict[timestamp], tags = remove_global_tags_not_present_in_both_sets(
            merged_dict[timestamp], tags, global_tags)
        merged_dict[timestamp] = merged_dict[timestamp].union(tags)
    return merged_dict


def read_vocublary_file(path):
    tags = []
    with open(path) as f:
        for line in f.readlines():
            tags.append(line.split(',')[0])
    return tags


@click.command()
@click.argument('path1', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('path2', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-o', '--output', 'output_path', type=click.Path(writable=True, resolve_path=True), help='output file', default=None)
@click.option('--global-tags', 'global_tags', help='comma seperated list of tags which have to be in both sets in order to survive like e.g. afk', default='')
def merge_tags(path1, path2, output_path, global_tags, controlled_vocabulary_file, error_file):
    '''merge tags from path1 and path2'''
    if controlled_vocabulary_file:
        controlled_vocabulary = read_vocublary_file(controlled_vocabulary_file)
    else:
        controlled_vocabulary = None
    print(controlled_vocabulary)
    global_tags = global_tags.split(',')
    dict1 = extract_tags_from_file(path1)
    dict2 = extract_tags_from_file(path2)
    merged_dict = merge_tag_dicts(dict1, dict2, global_tags)

    if output_path:
        write_tag_dict_to_file(output_path, merged_dict)
    else:
        print_tag_dict(merged_dict)


if __name__ == '__main__':
    merge_tags()
