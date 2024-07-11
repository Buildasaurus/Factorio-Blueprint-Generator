from flask import Flask, request, jsonify
import logging
import factoriocalc as fc
import factoriocalc.presets as fcc
import layout
import solver

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='myapp.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Initialize game configuration
def initialize_game():
    logger.debug('Initializing game configuration')
    fc.config.machinePrefs.set(fcc.MP_LATE_GAME)
    fc.config.machinePrefs.set([fc.mch.AssemblingMachine2()])
    logger.debug('Game configuration initialized successfully')

initialize_game()

def GenerateBlueprint(blueprint_input):
    '''This is copied from the mall_small test'''
    def writeText(text):
        with open("text_service.log", "a") as f:
            f.write(str(text) + "\n")

    try:
        writeText("Initializing blueprint generation")
        WIDTH = 64  # blueprint width
        HEIGHT = 64  # blueprint height

        # Input for the blueprint
        input_items = [fc.itm.iron_plate, fc.itm.copper_plate]

        # Output for the blueprint
        desired_output = fc.itm.electronic_circuit

        throughput = 3  # items per second. 3 is equivalent to 2 green circuits, 3 copper assembling 2 machines

        # Machines for construction - assembly types & smelting type
        factory = fc.produce(
            [desired_output @ throughput], using=input_items, roundUp=True
        ).factory

        site = layout.ConstructionSite(WIDTH, HEIGHT)
        machines = solver.randomly_placed_machines(factory, site.size())
        solver.add_connections(machines)
        solver.spring(machines, borders=((0, 0), (WIDTH, HEIGHT)))
        writeText("Machines are at: " + str([machine.position for machine in machines]))
        solver.machines_to_int(machines)
        writeText("Machines are at: " + str([machine.position for machine in machines]))
        solver.place_on_site(site, machines, None)
        writeText(str(site))
        blueprint_string = layout.site_as_blueprint_string(site, label="test of blueprint code")
        writeText(blueprint_string)
        writeText("End of test")
        return f"Blueprint generation complete: {blueprint_string}"
    except Exception as e:
        writeText(e)
        return f"failed to {e}"

@app.route('/process', methods=['POST'])
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
    app.run(host='0.0.0.0', port=5000, threaded=False)
