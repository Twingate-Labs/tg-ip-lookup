from argparse import ArgumentParser
from cloudlookup import CloudLookup


def main(ip):
    cl = CloudLookup()
    info = cl.lookup(ip)
    if info is None:
        print('Not found')
        pass
    print(info)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('ip', help='IP address to lookup')
    args = parser.parse_args()
    main(args.ip)
