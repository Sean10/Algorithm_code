#!/usr/bin/env python3
import argparse
import _direct
import _async
import _aio


def parser():
    """
    parser
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", "--file", type=str, help='file')
    argparser.add_argument("-c", "--count", type=int, help="repeat count")
    argparser.add_argument("-d", "--depth", type=int, help="depth")
    subparsers = argparser.add_subparsers(help="ioengine")
    parser_direct = subparsers.add_parser("direct")
    parser_direct.set_defaults(func=_direct.main_func)

    parser_async = subparsers.add_parser("async")
    parser_async.set_defaults(func=_async.main_func)

    parser_aio = subparsers.add_parser("aio")
    parser_aio.set_defaults(func=_aio.main_func)

    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    res = parser()
    res.func(**vars(res))
    print(res)
