'''This is a command line interface to the main functions found in the server.
It can be used for testing, or simply for scripting access to GERD featuers'''

import logging

import click

import analyze
import layout
import flow

# Set up logging
logging.basicConfig(filename='cli.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger()

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
    OPTIONAL_BLUEPRINT_KEYS = set(['item', 'label', 'description', 'entities', 'tiles', 'icons', 'schedules', 'stock_connections', 'version', 'wires'])
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

def show_blueprint_stats(bp_dict, show_entity_details):
    blueprint = bp_dict['blueprint']
    entities = blueprint['entities']

    # Title
    title = blueprint['label']
    click.echo(f'Title: {title}')

    # Version
    version_string = layout.factorio_version_int_as_string(blueprint['version'])
    click.echo(f'Factorio version: {version_string}')

    # Dimensions
    x_pos = [e['position']['x'] for e in entities]
    x0 = min(x_pos)
    x9 = max(x_pos)
    y_pos = [e['position']['y'] for e in entities]
    y0 = min(y_pos)
    y9 = max(y_pos)
    click.echo(f'Dimensions: ({x0}..{x9}, {y0}..{y9}) = {x9-x0} x {y9-y0}')

    # Description
    if 'description' not in blueprint:
        click.echo('Description: missing')
    else:
        click.echo('Description:')
        for line in blueprint['description'].split('\n'):
            click.echo(f'  {line}')

    # Entities
    if not show_entity_details:
        click.echo(f'Entities: {len(entities)}')
    else:
        import collections
        c = collections.Counter([
            e['name'] for e in entities
        ])
        click.echo('Entities:')
        for kind, count in c.most_common():
            click.echo(f'  {c[kind]} {kind}')
        click.echo(f'Total {c.total()}')

@click.group
def gerd():
    '''Command Line Interface access to some features of Gerd'''

@gerd.command
@click.argument('bp_file', type=click.types.Path(exists=True))
@click.option('-v', '--entity-details/--no-entity-details', default=False, help='Show entity count per type')
def stats(bp_file, entity_details):
    '''Show some blueprint statistics'''
    click.echo(f'Loading blueprint from "{bp_file}"')
    bp_dict = load_blueprint(bp_file)
    show_blueprint_stats(bp_dict, entity_details)

@gerd.command
@click.argument('bp_file', type=click.types.Path(exists=True))
def maxflow(bp_file):
    '''Compute the max flow reachable given a blueprint'''

    click.echo(f'Loading blueprint from "{bp_file}"')
    bp_dict = load_blueprint(bp_file)

    # Convert blueprint to flow graph
    G = analyze.extract_flow_from_blueprint(bp_dict)

    # Reduce flow to reflect max flow
    flow.compute_max_flow(G)

if __name__ == '__main__':
    gerd()
