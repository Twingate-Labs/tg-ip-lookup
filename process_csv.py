import csv
import shutil
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

from cloudlookup import CloudLookup
from progress.bar import IncrementalBar


read_fields = ['tenant id', 'tenant slug', 'network', 'connector', 'external ip']
write_fields = ['tenant id', 'tenant slug', 'network', 'connector', 'external ip', 'provider', 'region', 'asn_org']


def main(in_file, out_file, ip_field='external ip'):
    cl = CloudLookup()

    def process_row(row):
        if info := cl.lookup(row[ip_field]):
            row['provider'] = info.get('provider', '')
            row['region'] = info.get('region', '')
            row['asn_org'] = info.get('asn_org', '')
        return row

    temp_file = NamedTemporaryFile(mode='w', delete=False)

    with open(in_file, 'r') as csvfile, temp_file:
        bar = IncrementalBar('Rows', max=len(csvfile.readlines())-1)
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, fieldnames=read_fields)
        writer = csv.DictWriter(temp_file, fieldnames=write_fields)
        writer.writeheader()
        # skip header
        next(reader)
        for csv_row in reader:
            csv_row = process_row(csv_row)
            writer.writerow(csv_row)
            bar.next()
    bar.finish()
    shutil.move(temp_file.name, out_file)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('in_file', help='Path to input CSV file')
    parser.add_argument('out_file', help='Path to output CSV file')
    parser.add_argument('-ip', '--ip_field', required=False, help='Name of ip field', default='external ip')
    args = parser.parse_args()
    main(args.in_file, args.out_file, args.ip_field)
