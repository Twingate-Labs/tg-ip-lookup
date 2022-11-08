from collections import OrderedDict
import pickle
import os
import ipaddress
import geoip2.database


class CloudLookup:

    def __init__(self):
        pkg_dir = os.path.abspath(os.path.dirname(__file__))
        data_dir = os.path.join(pkg_dir, 'data')
        self.networks = CloudLookup.__load_data(data_dir)
        mm_asn_file = os.path.join(data_dir, 'GeoLite2-ASN.mmdb')
        # TODO: MM db needs to be closed - not an immediate problem
        self.mm_asn_reader = geoip2.database.Reader(mm_asn_file)

    @staticmethod
    def __load_data(data_dir) -> OrderedDict:
        data_file = os.path.join(data_dir, 'networks.pickle')
        with open(data_file, 'rb') as f:
            return pickle.load(f)

    def lookup(self, ip):
        ip_address = ipaddress.IPv4Address(ip)
        # Not the most efficient way to store or search but it is ok enough
        for network in self.networks:
            if ip_address in network:
                return self.networks[network]

        asn_response = self.mm_asn_reader.asn(ip)
        provider = ''
        asn_org = asn_response.autonomous_system_organization
        # Look away
        if asn_org.startswith('Hetzner'):
            provider = 'Hetzner'
        elif asn_org.startswith('DIGITALOCEAN'):
            provider = 'Digital Ocean'
        elif asn_org.startswith('Linode'):
            provider = 'Linode'
        elif 'Tencent' in asn_org:
            provider = 'Tencent'
        elif 'OVH' in asn_org:
            provider = 'OVH'
        elif 'SOFTLAYER' in asn_org:
            provider = 'IBM'
        elif asn_org == 'SPACEX-STARLINK':
            provider = 'Starlink'
        elif 'AS-CHOOPA' in asn_org:  # Not 100% certain
            provider = 'Vultr'
        elif 'Online S.a.s.' in asn_org:
            provider = 'Scaleway'
        elif 'Fly.io' in asn_org:
            provider = 'Fly.io'

        return {'provider': provider, 'region': '', 'asn_org': asn_org}
        pass

