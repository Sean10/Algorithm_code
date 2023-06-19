#!/usr/bin/env python3
from decoration import LazyImport
from logger import log
from common import *
import argparse


def parser():
    """
    parser
    """
    argparser = argparse.ArgumentParser()

    argparser.add_argument("-c", "--count", type=int, help="repeat count")
    argparser.add_argument("-d", "--depth", type=int, help="depth")
    argparser.add_argument("--io-type", type=str, help="io type")

    subparsers = argparser.add_subparsers(help="please choose ioengine", dest="engine")
    subparsers.add_parser("direct")
    subparsers.add_parser("async")
    subparser_aio = subparsers.add_parser("aio")
    subparser_aio.add_argument("-f", "--file", type=str, help="file")
    subparser_rbd = subparsers.add_parser("rbd")
    subparser_rbd.add_argument("-p", "--pool", type=str, help="pool name")
    subparser_rbd.add_argument("-c", "--conf", type=str, help="cluster config path")
    subparser_rbd.add_argument("-m", "--image", type=str, help="image name")
    subparser_rbd.add_argument("--image-count", type=int, help="image count")

    args = argparser.parse_args()
    res_dict = vars(args)
    return res_dict


if __name__ == "__main__":
    res = parser()
    rc = STATUS.E_OK
    if res['engine']:
        module = LazyImport(f"_{res['engine']}")        
        ret = module.main_func(**res)     
    exit(rc)