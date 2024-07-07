from concurrent import futures
from grpc_generated import service_pb2_grpc
from grpc_generated import service_pb2

import factoriocalc as fc
import factoriocalc.presets as fcc

import layout
import solver

class TextService(service_pb2_grpc.TextService):
    def DoText(self, request, context):
        f = open("demofile2.txt", "a")
        f.write("Now the file has more content!")
        f.close()
        result = "Doing text :D!"
        return service_pb2.TextThing(text=result)

    def GenerateBlueprint(self,request, context):
        '''This is copied from the mall_small test'''
        def writeText(text):
            f = open("text_service_log.txt", "a")
            f.write(text + "\n")
            f.close()

        try:
            writeText("Initializing blueprint generation")
            WIDTH = 64 # blueprint width
            HEIGHT = 64 # blueprint heigh
            # Input for the blueprint
            # Input for the blueprint
            input_items = [fc.itm.iron_plate, fc.itm.copper_plate]

            # Output for the blueprint
            desired_output = fc.itm.electronic_circuit

            throughput = 3  # items pr second. 3 is equivalent of 2 green circuit, 3 copper assembling 2 machines

            # machines for construciton - assemblytypes & smelting type
            fc.config.machinePrefs.set(fcc.MP_LATE_GAME)
            fc.config.machinePrefs.set([fc.mch.AssemblingMachine2()])
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
            writeText(layout.site_as_blueprint_string(site, label="test of blueprint code"))
            writeText("End of test")
            return service_pb2.TextThing(text="complete")
        except Exception as e:
            return service_pb2.TextThing(text=f"failed to {e}")





a = TextService()
print(TextService.GenerateBlueprint(1,2,3))
