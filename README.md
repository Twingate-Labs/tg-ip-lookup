# Lookup an IP address to find out which public cloud it originates from

This repository contains python3 code to find out which public cloud an IP address originates from.

## Requirements
* Python3 (3.11)
* MaxMind license key (for [GeoLite2 ASN](https://dev.maxmind.com/geoip/docs/databases/asn) database). *This database is free subject to license restrictions by MaxMind*. Sign up [here](https://www.maxmind.com/en/geolite2/signup).
* see also [requirements.txt](requirements.txt)

## Supported Clouds
* Amazon Web Services (AWS)
* Google Cloud Platform (GCP)
* Microsoft Azure
* Oracle Cloud Infrastructure (OCI)
* Hetzner
* DigitalOcean
* Linode
* Tencent
* OVH
* IBM Cloud
* Vultr
* Scaleway
* Fly.io
* Starlink (yes ok, not a cloud but it is up in the clouds right?)

### How it works
For AWS, GCP, Azure and OCI this looks up the IPs using the publicly published IP ranges by these providers.

For the other providers it uses the MaxMind ASN database to lookup IP information.

Internally this is using the `ipaddress` module in python to do a search through the various CIDR blocks. In future this could be improved if the need arises.

## Install Using Python Pip
1. pip install tg_ip_lookup
2. Prepare the database, execute `python -c "exec(\"import tg_ip_lookup\ntg_ip_lookup.cloudlookup.loadCloudProviderData.main(\'*MaxMind License Key*\')\")"`
3. Try an IP lookup `python -c "exec(\"import tg_ip_lookup\ntg_ip_lookup.main(\'XXX.XXX.XXX.XXX\')\")"`

### Manual Setup
1. Clone this repo: `git clone https://github.com/Twingate-Labs/tg-ip-lookup`, & switch into directory
2. Install requirements (virtual env recommended), e.g. `pip install -r requirements.txt`
3. Prepare the database `python cloudlookup/loadCloudProviderData.py *MaxMind License Key*`. The database should be updated regularly (e.g. daily)
4. Try an IP lookup, e.g. `python lookup_ip.py XXX.XXX.XXX.XXX`