from concurrent import futures
import logging

import grpc
import add_pb2
import add_pb2_grpc


class Add(add_pb2_grpc.AddServicer):

    def AddTwo(self, request, context):
        s = request.opone + request.optwo
        return add_pb2.AddReply(result = s)


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_pb2_grpc.add_AddServicer_to_server(Add(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
