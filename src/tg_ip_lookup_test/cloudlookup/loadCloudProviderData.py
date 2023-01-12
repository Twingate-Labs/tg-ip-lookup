import ipaddress
import os
import pickle
import tarfile
from argparse import ArgumentParser
from collections import OrderedDict
from pathlib import Path
from tempfile import NamedTemporaryFile

import jmespath
import requests
from bs4 import BeautifulSoup
from jmespath import functions


class CustomJmesFunctions(functions.Functions):

    def __init__(self, context=None):
        super().__init__()
        self.data = {}

    @functions.signature({'types': ['string']}, {'types': ['string']})
    def _func_store(self, s, var):
        """
            stores value s in the variable var. can later be retrieved using fetch
        """
        self.data[var] = s
        return s

    @functions.signature({'types': ['string']})
    def _func_fetch(self, var):
        """
            returns variable var or None
        """
        return self.data.get(var, None)

    @functions.signature({'types': ['array'], 'variadic': True})
    def _func_zip(self, *arguments):
        return list(map(list, zip(*arguments)))

    @functions.signature({'types': ['array']})
    def _func_from_items(self, pairs):
        return dict(pairs)


options = jmespath.Options(custom_functions=CustomJmesFunctions())


def load_networks(url, jmes_expression):
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        ranges = jmespath.search(jmes_expression, data, options)
        result = sorted({ipaddress.IPv4Network(k): v for k, v in ranges.items()}.items())
        return result
    pass


def lookup_microsoft_download_url(url):
    page = requests.get(url)
    # parse HTML to get the real link
    soup = BeautifulSoup(page.content, 'html.parser')
    download_url = soup.find('a', {'data-bi-containername': 'download retry'})['href']
    return download_url


def main( max_mind_key):
    pkg_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(pkg_dir, "data")
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    networks = OrderedDict()

    print("Processing AWS ranges...")
    aws_info = load_networks('https://ip-ranges.amazonaws.com/ip-ranges.json',
                             'from_items(zip( prefixes[?ip_prefix].ip_prefix, prefixes[?ip_prefix].{provider: \'AWS\', region: region, service: service} ))')
    for [k, v] in aws_info:
        networks[k] = v

    print("Processing GCP ranges...")
    gcp_info = load_networks('https://www.gstatic.com/ipranges/cloud.json',
                             'from_items(zip( prefixes[?ipv4Prefix].ipv4Prefix, prefixes[?ipv4Prefix].{provider: \'GCP\', region: scope} ))')
    for [k, v] in gcp_info:
        networks[k] = v

    # Azure See https://learn.microsoft.com/en-us/azure/virtual-network/service-tags-overview
    # Azure Public
    print("Processing Azure ranges...")
    azure_public_info = load_networks(lookup_microsoft_download_url('https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'),
                                      'values[].properties | @[].{s: store(systemService, \'service\'), r: store(region, \'region\'), a: addressPrefixes[?contains(@, \'.\')][@, '
                                      '{provider: \'Azure (Public)\', service: fetch(\'service\'), region: fetch(\'region\')}]} | sort_by(@[], &r) | from_items(@[].a[])')
    for [k, v] in azure_public_info:
        networks[k] = v

    # Azure US Gov Cloud
    azure_usgov_info = load_networks(lookup_microsoft_download_url('https://www.microsoft.com/en-us/download/confirmation.aspx?id=57063'),
                                      'values[].properties | @[].{s: store(systemService, \'service\'), r: store(region, \'region\'), a: addressPrefixes[?contains(@, \'.\')][@, '
                                      '{provider: \'Azure (US Gov)\', service: fetch(\'service\'), region: fetch(\'region\')}]} | sort_by(@[], &r) | from_items(@[].a[])')
    for [k, v] in azure_usgov_info:
        networks[k] = v

    # Azure China 21 Vianet
    azure_china_info = load_networks(lookup_microsoft_download_url('https://www.microsoft.com/en-us/download/confirmation.aspx?id=57062'),
                                      'values[].properties | @[].{s: store(systemService, \'service\'), r: store(region, \'region\'), a: addressPrefixes[?contains(@, \'.\')][@, '
                                      '{provider: \'Azure (China)\', service: fetch(\'service\'), region: fetch(\'region\')}]} | sort_by(@[], &r) | from_items(@[].a[])')
    for [k, v] in azure_china_info:
        networks[k] = v

    # Azure Germany
    azure_germany_info = load_networks(lookup_microsoft_download_url('https://www.microsoft.com/en-us/download/confirmation.aspx?id=57064'),
                                      'values[].properties | @[].{s: store(systemService, \'service\'), r: store(region, \'region\'), a: addressPrefixes[?contains(@, \'.\')][@, '
                                      '{provider: \'Azure (Germany)\', service: fetch(\'service\'), region: fetch(\'region\')}]} | sort_by(@[], &r) | from_items(@[].a[])')
    for [k, v] in azure_germany_info:
        networks[k] = v

    print("Processing OCI ranges...")
    # Oracle Cloud - see https://docs.oracle.com/en-us/iaas/Content/General/Concepts/addressranges.htm
    oci_info = load_networks('https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json',
                             'regions[].{r: store(region, \'region\'), a: cidrs[].[cidr, {provider: \'OCI\', region: fetch(\'region\')}]} | from_items(@[].a[])')
    for [k, v] in oci_info:
        networks[k] = v

    # IBM Cloud - see https://github.com/ibm-cloud-docs/cloud-infrastructure/blob/master/ips.md
    # Public IPs parsed from Markdown table to JSON manually using https://tableconvert.com/markdown-to-json
    # ibm_cloud_json = [{"Data center":"ams03","City":"Amsterdam","IP range":"159.8.198.0/23"},{"Data center":"che01","City":"Chennai","IP range":"169.38.118.0/23"},{"Data center":"dal05","City":"Dallas","IP range":"173.192.118.0/23"},{"Data center":"dal08","City":"Dallas","IP range":"192.255.18.0/24"},{"Data center":"dal09","City":"Dallas","IP range":"198.23.118.0/23"},{"Data center":"dal10","City":"Dallas","IP range":"169.46.118.0/23"},{"Data center":"dal12","City":"Dallas","IP range":"169.47.118.0/23"},{"Data center":"dal13","City":"Dallas","IP range":"169.48.118.0/24"},{"Data center":"fra02","City":"Frankfurt","IP range":"159.122.118.0/23"},{"Data center":"fra04","City":"Frankfurt","IP range":"161.156.118.0/24"},{"Data center":"fra05","City":"Frankfurt","IP range":"149.81.118.0/23"},{"Data center":"lon02","City":"London","IP range":"5.10.118.0/23"},{"Data center":"lon04","City":"London","IP range":"158.175.127.0/24"},{"Data center":"lon05","City":"London","IP range":"141.125.118.0/23"},{"Data center":"lon06","City":"London","IP range":"158.176.118.0/23"},{"Data center":"mil01","City":"Milan","IP range":"159.122.138.0/23"},{"Data center":"mon01","City":"Montreal","IP range":"169.54.118.0/23"},{"Data center":"osa21","City":"Osaka","IP range":"163.68.118.0/24"},{"Data center":"osa22","City":"Osaka","IP range":"163.69.118.0/24"},{"Data center":"osa23","City":"Osaka","IP range":"163.73.118.0/24"},{"Data center":"par01","City":"Paris","IP range":"159.8.118.0/23"},{"Data center":"sao01","City":"São Paulo","IP range":"169.57.138.0/23"},{"Data center":"sjc01","City":"San Jose","IP range":"50.23.118.0/23"},{"Data center":"sjc03","City":"San Jose","IP range":"169.45.118.0/23"},{"Data center":"sjc04","City":"San Jose","IP range":"169.62.118.0/24"},{"Data center":"sng01","City":"Jurong East","IP range":"174.133.118.0/23"},{"Data center":"syd01","City":"Sydney","IP range":"168.1.18.0/23"},{"Data center":"syd04","City":"Sydney","IP range":"130.198.118.0/23"},{"Data center":"syd05","City":"Sydney","IP range":"135.90.118.0/23"},{"Data center":"tok02","City":"Tokyo","IP range":"161.202.118.0/23"},{"Data center":"tok04","City":"Tokyo","IP range":"128.168.118.0/23"},{"Data center":"tok05","City":"Tokyo","IP range":"165.192.118.0/23"},{"Data center":"tor01","City":"Toronto","IP range":"158.85.118.0/23"},{"Data center":"tor04","City":"Toronto","IP range":"163.74.118.0/23"},{"Data center":"tor05","City":"Toronto","IP range":"163.75.118.0/23"},{"Data center":"wdc01","City":"Washington D.C.","IP range":"208.43.118.0/23"},{"Data center":"wdc03","City":"Washington D.C.","IP range":"192.255.38.0/24"},{"Data center":"wdc04","City":"Washington D.C.","IP range":"169.55.118.0/23"},{"Data center":"wdc06","City":"Washington D.C.","IP range":"169.60.118.0/23"},{"Data center":"wdc07","City":"Washington D.C.","IP range":"169.61.118.0/23"}]
    # ibm_cloud_ranges = jmespath.search('from_items(@[].["IP range", {provider: \'IBM Cloud\', region: "Data center"}])', ibm_cloud_json, options)
    # ibm_info = sorted({ipaddress.IPv4Network(k): v for k, v in ibm_cloud_ranges.items()}.items())
    # for [k, v] in ibm_info:
    #     networks[k] = v

    # MaxMind ASN Db
    if max_mind_key is not None:
        print("Downloading MaxMind GeoLite ASN database...")
        max_mind_url = f'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN&license_key={max_mind_key}&suffix=tar.gz'
        with requests.get(max_mind_url, stream=True) as response, NamedTemporaryFile(mode='wb', delete=True) as temp_file:
            if response.status_code == 200:
                temp_file.write(response.raw.read())
                with tarfile.open(name=temp_file.name, mode='r:gz') as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            member.path = '/'.join(member.path.split('/')[1:])
                            tar_file.extract(member, data_dir)
    else:
        print('MaxMind key not specified, skipping.')

    output_file = os.path.join(data_dir, 'networks.pickle')
    with open(output_file, 'wb') as f:
        pickle.dump(networks, f)
    print(f'Data saved to "{data_dir}"')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('max_mind_key', nargs='?', help='MaxMind license key', default=None)
    args = parser.parse_args()
    main(args.max_mind_key)
