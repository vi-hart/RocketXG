import argparse
from database.builder import RLCSParser

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str)
parser.add_argument("-o", "--output", type=str)
parser.add_argument("-u", "--dburl", type=str)
args = parser.parse_args()
db = RLCSParser(database_url=args.dburl, parsed_dir=args.output)
db.process_directory(args.input)
