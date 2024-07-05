from concurrent import futures
import numpy as np
from grpc_generated import service_pb2_grpc
from grpc_generated import service_pb2

class TextService(service_pb2_grpc.TextService):
    '''Expecting request to be a string'''
    def DoText(self, request, context):
        print(f"Received {request} as string")
        result = request.text + " added text!"
        return service_pb2.TextThing(text=result)
