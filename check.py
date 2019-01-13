#!/usr/bin/env python
import click
from merge import extract_tags_from_file


@click.command()
@click.argument('tag_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('controlled_vocabulary_file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--error-file', 'error_file', type=click.Path(exists=True, readable=True, resolve_path=True), default=None, help='path to file in which errors are reported')
def check_tags(tag_file, controlled_vocabulary_file, error_file):
    '''check if tags are part of controlled vocabulary'''
    controlled_vocabulary = []
    with open(controlled_vocabulary_file) as f:
        for line in f.readlines():
            controlled_vocabulary.append(line.split(',')[0])
    tag_dict = extract_tags_from_file(tag_file)
    for timestamp, tags in tag_dict.items():
        for tag in tags:
            if tag not in controlled_vocabulary:
                error = '{} at {} in {} is not in controlled vocabulary'.format(
                    tag, timestamp, tag_file)
                if error_file:
                    with open(error_file, 'a') as f:
                        f.write('\n* ' + error + '\n')
                else:
                    raise ValueError(error)


if __name__ == '__main__':
    check_tags()
