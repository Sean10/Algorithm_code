#!/usr/bin/env python3
from decoration import LazyImport
from logger import log
import argparse


def parser():
    """
    parser
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", "--file", type=str, help="file")
    argparser.add_argument("-c", "--count", type=int, help="repeat count")
    argparser.add_argument("-d", "--depth", type=int, help="depth")
    subparsers = argparser.add_subparsers(help="please choose ioengine", dest="engine", required=True)
    parser_direct = subparsers.add_parser("direct")
    parser_async = subparsers.add_parser("async")
    parser_aio = subparsers.add_parser("aio")
    parser_rbd = subparsers.add_parser("rbd")

    args = argparser.parse_args()
    res_dict = vars(args)
    return res_dict


if __name__ == "__main__":
    res = parser()
    ret = 0
    if res['engine']:
        module = LazyImport(f"_{res['engine']}")        
        ret = module.main_func(**res)
        
    exit(ret)