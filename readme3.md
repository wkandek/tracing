Tracing Part III

[gGRPC](https://grpc.io/) is remote procedure call framework that is supported by OpenTelemetry natively.

Let's rewrite our calc program to use grpc in its calls to perform math operations.

We will go in steps:
- get the python HelloWorld gRPC demo working
- rewrite HelloWorld to a simple Add numbers program
- rewrite calc to use gRPC, using the knowledge from Add

The HelloWorld gRPC demo is described in the [python quickstart](https://grpc.io/docs/languages/python/quickstart/) page. The code itself is contained in the larger repository described there.
Alternative the 3 files needed (helloworld.proto, greeter_server.py, greeter_client.py) are incldued in this repository as well.

Here are the necessary steps once you have the files:
- mkdir helloworld; cd helloworld
- python3 -m venv .
- source bin/activate
- pip3 install grpcio grpcio-tools
- create/copy files helloworld.proto, greeter_server.py, greeter_client.py
- python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./helloworld.proto # this creates the sub files fro grpc that are included the the pytohn greeter programs
- in 2 seperate terminal windows run
  python3 greeter_server.py
  python3 greeter_client.py
  
greeter_client.py sends the string "you" to the server, the server answers with "Hello you!" all this using gRPC.
  

