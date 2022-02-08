#!/usr/bin/env python3
import argparse
import direct



def parser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", "--file", type=str, help='file')
    argparser.add_argument("-c", "--count", type=int, help="repeat count")
    subparsers = argparser.add_subparsers(help="direct")
    parser_sync = subparsers.add_parser("direct")
    parser_sync.set_defaults(func=direct.main_func)
    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    res = parser()
    res.func(**vars(res))
    print(res)
