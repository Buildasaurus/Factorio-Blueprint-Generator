from concurrent import futures
from grpc_generated import service_pb2_grpc
from grpc_generated import service_pb2

import factoriocalc

class TextService(service_pb2_grpc.TextService):
    def DoText(self, request, context):
        result = "Doing text :D!"
        return service_pb2.TextThing(text=result)

    def GenerateBlueprint(self,request, context):
        result = "Blueprint :O"
        return service_pb2.TextThing(text=result)
