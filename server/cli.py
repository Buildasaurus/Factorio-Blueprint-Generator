'''This is a command line interface to the main functions found in the server.
It can be used for testing, or simply for scripting access to GERD featuers'''

import click

import analyze
import layout

def load_blueprint(filename):
    '''Load and validate a string-encoded blueprint from a file.'''

    # Load data
    with open(filename) as fi:
        data = fi.read()
        bp_dict = layout.import_blueprint_dict(data)

    # Validate data
    if list(bp_dict.keys()) != ['blueprint']:
        raise ValueError(f'Expected a blueprint, but root JSON keys are: {list(bp_dict.keys())}')
    blueprint = bp_dict['blueprint']
    OPTIONAL_BLUEPRINT_KEYS = set(['item', 'label', 'description', 'entities', 'tiles', 'icons', 'schedules', 'version', 'wires'])
    MANDATORY_BLUEPRINT_KEYS = set(['item','entities', 'icons', 'version'])
    found_blueprint_keys = set(blueprint.keys())
    missing_keys = MANDATORY_BLUEPRINT_KEYS - found_blueprint_keys
    extra_keys = found_blueprint_keys - MANDATORY_BLUEPRINT_KEYS - OPTIONAL_BLUEPRINT_KEYS
    if len(missing_keys) > 0:
        print(f'Blueprint keys: {found_blueprint_keys}')
        raise ValueError(f'Blueprint missing keys: {missing_keys}')
    if len(extra_keys) > 0:
        print(f'Blueprint keys: {found_blueprint_keys}')
        raise ValueError(f'Blueprint unknown keys: {extra_keys}')

    return bp_dict

@click.group
def gerd():
    '''Command Line Interface access to some features of Gerd'''

@gerd.command
@click.argument('bp_file', type=click.types.Path(exists=True))
def maxflow(bp_file):
    '''Compute the max flow reachable given a blueprint'''

    click.echo(f'Loading blueprint from "{bp_file}"')
    bp_dict = load_blueprint(bp_file)

    # Convert blueprint to flow graph
    G = analyze.extract_flow_from_blueprint(bp_dict)

if __name__ == '__main__':
    gerd()