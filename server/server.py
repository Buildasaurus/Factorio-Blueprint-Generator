import logging

from flask import request, jsonify
import connexion
import factoriocalc as fc
import factoriocalc.presets as fcc

import layout
import solver

# Set up logging
logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Initialize server
app = connexion.FlaskApp(__name__)
app.add_api('fbg-api.yaml')


def GenerateBlueprint(blueprint_input):
    '''This is copied from the mall_small test'''
    try:
        logger.info('Starting blueprint generation process')
        logger.debug('Initializing game configuration')

        fc.config.machinePrefs.set(fcc.MP_LATE_GAME)
        fc.config.machinePrefs.set([fc.mch.AssemblingMachine2()])

        WIDTH = 64  # blueprint width
        HEIGHT = 64  # blueprint height

        input_items = [fc.itm.iron_plate, fc.itm.copper_plate]
        desired_output = fc.itm.electronic_circuit
        throughput = 3  # items per second. 3 is equivalent to 2 green circuits, 3 copper assembling 2 machines

        logger.debug('Game configuration initialized successfully')
        logger.debug('Generating blueprint')

        # Machines for construction - assembly types & smelting type
        factory = fc.produce(
            [desired_output @ throughput], using=input_items, roundUp=True
        ).factory

        site = layout.ConstructionSite(WIDTH, HEIGHT)
        machines = solver.randomly_placed_machines(factory, site.size())
        solver.add_connections(machines)

        solver.spring(machines, borders=((0, 0), (WIDTH, HEIGHT)))
        logger.debug("Machines are at: " + str([machine.position for machine in machines]))

        solver.machines_to_int(machines)
        logger.debug("Machines as integers are at: " + str([machine.position for machine in machines]))

        logger.debug("Placing on site")
        solver.place_on_site(site, machines, None)
        logger.debug(str(site))

        blueprint_string = layout.site_as_blueprint_string(site, label="test of blueprint code")
        logger.debug(f"Generated following blueprint string: {blueprint_string}")
        logger.info('Completed blueprint generation process')

        return f"Blueprint generation complete: {blueprint_string}"
    except Exception as e:
        logger.error(e)
        return f"failed to {e}"

#@app.route('/process', methods=['POST'])
# with Connexion, the fbg-api.yaml file specifies how to route endpoints to functions 
def process_string():
    data = request.json
    input_string = data.get('input_string')
    if not input_string:
        return jsonify({'error': 'No input string provided'}), 400

    # Process the input string
    blueprint_output = GenerateBlueprint(input_string)
    output_string = f"Hi again! {blueprint_output} input: {input_string}"

    return jsonify({'output_string': output_string})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
