#!/usr/local/Cellar/mitmproxy/2.0.2_1/libexec/bin/mitmdump -s

from __future__ import print_function

import os
from urllib.parse import urlsplit
#import mitmproxy
import mitmproxy
#http.HTTPRequest

def response(flow):
    #res = mitmproxy.http.HTTPResponse()
    # print(flow.request.method + " " + flow.request.path)
    # for k, v in flow.request.headers.items():
    #     print("%-20s: %s" % (k.upper(), v))
    #
    # print("-"*50 + "response headers:")
    # for k, v in flow.response.headers.items():
    #     print("%-20s: %s" % (k.upper(), v))
    #     print("-"*50 + "request headers:")

    print(flow.response.headers['Content-Type'])
    print(urlsplit(flow.request.url))
    if flow.response.headers['Content-Type'].startswith('image/'):
      url = urlsplit(flow.request.url)
      name = os.path.basename(url.path)
      with open(name, 'wb') as f:
        f.write(flow.response.content)
      print(name, 'written')
