#!/bin/python

import argparse

def execute():
    """ Execute the script, see module docstring for more details """
    parser = argparse.ArgumentParser(description=globals()['__doc__'])

    parser.add_argument('string', help='The sentence to convert')
    args = parser.parse_args()

    result = ""
    for l in args.string.lower():
        if ord("a")<=ord(l)<=ord("z"):
            result += chr((ord(l)-ord("a")+13)%26+ord("a"))
        else:
            result += l
    print(result)

execute()
