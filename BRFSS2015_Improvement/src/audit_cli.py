"""Audit-only entry point; works without sklearn, scipy, joblib or boosting."""
import argparse
from audit_commands import inspect, audit_codes

def main():
    parser=argparse.ArgumentParser()
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ['inspect','audit-codes']:
        p=commands.add_parser(name)
        p.add_argument('--data',required=True);p.add_argument('--schema',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args()
    {'inspect':inspect,'audit-codes':audit_codes}[args.command](args)
if __name__=='__main__':main()
