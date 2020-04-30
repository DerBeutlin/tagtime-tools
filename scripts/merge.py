#!/usr/bin/env python
import click
from tagtime.merge import extract_tags_from_file, merge_tag_dicts, write_tag_dict_to_file, print_tag_dict


@click.command()
@click.argument('path1',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.argument('path2',
                type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-o',
              '--output',
              'output_path',
              type=click.Path(writable=True, resolve_path=True),
              help='output file',
              default=None)
@click.option(
    '--global-tags',
    'global_tags',
    help=
    'comma seperated list of tags which have to be in both sets in order to survive like e.g. afk',
    default='')
def merge_tags(path1, path2, output_path, global_tags):
    '''merge tags from path1 and path2'''
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
