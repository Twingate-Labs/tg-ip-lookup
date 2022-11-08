# Lookup an IP address to find out which public cloud it originates from

This repository contains python3 code to find out which public cloud an IP addres originates from.

## Requirements
* Python3 (3.11)
* MaxMind license key (for [GeoLite2 ASN](https://dev.maxmind.com/geoip/docs/databases/asn) database). *This database is free subject to license restrictions by MaxMind*.
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
* Starlink

### How it works
For AWS, GCP, Azure and OCI this looks up the IPs using the publicly published IP ranges by these providers.

For the other providers it uses the MaxMind ASN database to lookup IP information.

### Setup
1. Clone this repo: `git clone https://github.com/Twingate-Labs/tg-ip-lookup`
2. Install requirements (virtual env recommended), e.g. `pip install -r requirements.txt`
3. Prepare the database `python cloudlookup/loadCloudProviderData.py *MaxMind License Key*`
4. Try an IP lookup, e.g. `python lookup_ip.py XXX.XXX.XXX.XXX`