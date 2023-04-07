from __future__ import print_function

import logging

import grpc
import add_pb2
import add_pb2_grpc


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Will try to add ...")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = add_pb2_grpc.AddStub(channel)
        response = stub.AddTwo(add_pb2.AddRequest(opone=2,optwo=4))
    print("Add client received: ", response.result)


if __name__ == '__main__':
    logging.basicConfig()
    run()
