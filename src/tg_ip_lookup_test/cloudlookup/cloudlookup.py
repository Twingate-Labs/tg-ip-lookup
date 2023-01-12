from collections import OrderedDict
import pickle
import os
import ipaddress
import geoip2.database
import weakref


class CloudLookup:

    def __init__(self):
        pkg_dir = os.path.abspath(os.path.dirname(__file__))
        data_dir = os.path.join(pkg_dir, 'data')
        self.networks = CloudLookup.__load_data(data_dir)
        mm_asn_file = os.path.join(data_dir, 'GeoLite2-ASN.mmdb')
        if os.path.isfile(mm_asn_file):
            self.mm_asn_reader = geoip2.database.Reader(mm_asn_file)
            self._finalizer = weakref.finalize(self, self.mm_asn_reader.close)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def lookup(self, ip):
        # Inspired from: https://netaddr.readthedocs.io/en/latest/_modules/netaddr/ip/sets.html#IPSet.__contains__ :
        # Iterating over all possible supernets loops at most 32 times for IPv4 or 128 times for IPv6,
        # no matter how many CIDRs this object contains.
        # See also: https://discuss.python.org/t/ipset-in-scope-for-stdlib-ipaddress/7147
        ip_network = ipaddress.IPv4Network(ip)
        while ip_network.prefixlen:
            if provider := self.networks.get(ip_network):
                return provider
            ip_network = ip_network.supernet(1)
        if hasattr(self, 'mm_asn_reader'):
            asn_response = self.mm_asn_reader.asn(ip)
            return self.__asn_org_to_provider(asn_response.autonomous_system_organization)

    # This is a naive lookup
    def lookup_old(self, ip):
        ip_address = ipaddress.IPv4Address(ip)
        # Not the most efficient way to store or search, but it is ok enough
        for network in self.networks:
            if ip_address in network:
                return self.networks[network]
        if hasattr(self, 'mm_asn_reader'):
            asn_response = self.mm_asn_reader.asn(ip)
            return self.__asn_org_to_provider(asn_response.autonomous_system_organization)

    @staticmethod
    def __load_data(data_dir) -> OrderedDict:
        data_file = os.path.join(data_dir, 'networks.pickle')
        with open(data_file, 'rb') as f:
            return pickle.load(f)

    def close(self):
        if hasattr(self, '_finalizer'):
            self._finalizer()

    @staticmethod
    def __asn_org_to_provider(asn_org, other_label=''):
        provider = other_label
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
