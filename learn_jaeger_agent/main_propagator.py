#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-18 15:12
# @Author  : sean10
# @Site    :
# @File    : main.py
# @Software: PyCharm

"""
use jaeger agent to trace.

"""


import logging
import time
from opentracing import Tracer, Format
from jaeger_client import Config
import sys

if __name__ == "__main__":
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

    config = Config(
        config={  # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': '127.0.0.1',
                'reporting_port': '6831',
            },
            'logging': True,
        },
        service_name='second propagator with subprocess',
        validate=True,
    )
    # if len(sys.argv) < 2:
    #     sys.exit(1)
    tracer = config.initialize_tracer()
    # print(tracer.debug_id_header)

    # tracer = Tracer()

    if len(sys.argv) >= 2:
        import json

        carrier = json.loads(sys.argv[1])

        print(sys.argv)

        span_context = tracer.extract(Format.TEXT_MAP, carrier)
    else:
        # span_context = tracer.start_active_span("new")
        pass
    # this call also sets opentracing.tracer
    # print(tracer.debug_id_header)



    with tracer.start_active_span('new', child_of=span_context, finish_on_close=True) as scope:
        scope.span.log_kv({'event': 'test message', 'life': 40})

        with tracer.start_active_span('ChildSpan') as child_span:

            child_span.span.log_kv({'event': 'down below'})
            # time.sleep(2)

        # time.sleep(5)   # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50

        scope.span.log_kv({'event': 'test message', 'life': 39})
        # temp = {}
        # tracer.inject(scope.span.context, "text_map",temp)
        # print(temp)
    # time.sleep(2)
    if len(sys.argv) < 2:
        pass
        # span_context.close()
    time.sleep(2)
    # tracer.close()
    # tracer.close()  # flush any buffered spans
#
# from grpc_opentracing import open_tracing_client_interceptor, ActiveSpanSource
# from grpc_opentracing.grpcext import intercept_channel
# from jaeger_client import Config
#
# # dummy class to hold span data for passing into GRPC channel
# class FixedActiveSpanSource(ActiveSpanSource):
#
#     def __init__(self):
#         self.active_span = None
#
#     def get_active_span(self):
#         return self.active_span
#
# config = Config(
#     config={
#         'sampler': {
#             'type': 'const',
#             'param': 1,
#         },
#         'logging': True,
#     },
#     service_name='foo')
#
# tracer = config.initialize_tracer()
#
# # ...
# # In the method where GRPC requests are sent
# # ...
# active_span_source = FixedActiveSpanSource()
# tracer_interceptor = open_tracing_client_interceptor(
#     tracer,
#     log_payloads=True,
#     active_span_source=active_span_source)
#
# with tracer.start_span('span-foo') as span:
#     print(f"Created span: trace_id:{span.trace_id:x}, span_id:{span.span_id:x}, parent_id:{span.parent_id}, flags:{span.flags:x}")
#     # provide the span to the GRPC interceptor here
#     active_span_source.active_span = span
#     with grpc.insecure_channel(...) as channel:
#         channel = intercept_channel(channel, tracer_interceptor)