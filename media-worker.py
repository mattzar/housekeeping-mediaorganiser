
import argparse
from settings import defaults
from MediaSorter import *

def arg_handler():

    parser = argparse.ArgumentParser(description="A program to sort media")
    parser.add_argument("-v", "--verbose", help="enable verbose mode", action="store_true")
    parser.add_argument("-i", "--input", help="path to source directory")
    parser.add_argument("-o", "--output", help="path to output directory")
    parser.add_argument("-l", "--log", help="path to log output file")
    parser.add_argument("-n", "--include", help="filetypes to include in sort")
    parser.add_argument("-x", "--exclude", help="wildcarded names to exclude")

    return parser.parse_args()

def main():

    args = arg_handler()

    sorter = MediaSorter()
    job = sorter.prepare_job(args)
    sorter.process_job(job)

if __name__ == '__main__':
    main()