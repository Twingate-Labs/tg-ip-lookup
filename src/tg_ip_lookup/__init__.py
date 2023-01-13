from argparse import ArgumentParser
from .cloudlookup.cloudlookup import CloudLookup


def main(ip):
    # Constructing a CloudLookup is expensive so in real-world scenarios try to reuse instances
    with CloudLookup() as cl:
        if info := cl.lookup(ip):
            print(info)
        else:
            print('Not found')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('ip', help='IP address to lookup')
    args = parser.parse_args()
    main(args.ip)
