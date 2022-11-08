from argparse import ArgumentParser
from cloudlookup import CloudLookup


def main(ip):
    cl = CloudLookup()
    if info := cl.lookup(ip):
        print(info)

    print('Not found')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('ip', help='IP address to lookup')
    args = parser.parse_args()
    main(args.ip)
