from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("edpservers")


@tracer.start_as_current_span("add")
def add(a,b):
  return a+b

@tracer.start_as_current_span("subtract")
def subtract(a,b):
  return a-b

# main
s = add(1,2)
s = subtract(s,4)
s = add(s,5)
print(s)


