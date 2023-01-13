import csv
import shutil
import time
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

from cloudlookup import CloudLookup
from progress.bar import IncrementalBar


def main(in_file, out_file, ip_field='external ip'):

    temp_file = NamedTemporaryFile(mode='w', delete=False)

    start_time = time.time()
    with open(in_file, 'r') as csv_file, CloudLookup() as cl, temp_file:
        bar = IncrementalBar('Rows', max=len(csv_file.readlines())-1)
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        if ip_field not in reader.fieldnames:
            print(f'Column "{ip_field}" not found in file "{in_file}".')
            return
        write_fields = reader.fieldnames.copy()
        write_fields.extend(['provider', 'region', 'asn_org'])
        writer = csv.DictWriter(temp_file, fieldnames=write_fields)
        writer.writeheader()
        for csv_row in reader:
            if info := cl.lookup(csv_row[ip_field]):
                csv_row['provider'] = info.get('provider', '')
                csv_row['region'] = info.get('region', '')
                csv_row['asn_org'] = info.get('asn_org', '')
            writer.writerow(csv_row)
            bar.next()
    bar.finish()
    elapsed_time = time.time() - start_time
    print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    shutil.move(temp_file.name, out_file)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('in_file', help='Path to input CSV file')
    parser.add_argument('out_file', help='Path to output CSV file')
    parser.add_argument('-ip', '--ip_field', required=False, help='Name of ip field', default='external ip')
    args = parser.parse_args()
    main(args.in_file, args.out_file, args.ip_field)
