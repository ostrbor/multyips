import netifaces
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_toolbelt.adapters.source import SourceAddressAdapter
import requests

URL = 'https://www.google.com'


def get_ips():
    # learn how to choose ips that you need to send requests
    ips = []
    for ifs in netifaces.interfaces():
        result = netifaces.ifaddresses(ifs)
        if result.get(netifaces.AF_INET):
            for ip in result[netifaces.AF_INET]:
                ips.append(ip['addr'])
    return ips


def connect_google(ip):
    with requests.Session() as s:
        s.mount('http://', SourceAddressAdapter(ip))
        s.mount('https://', SourceAddressAdapter(ip))
        try:
            resp = s.get(URL)
            return resp
        except requests.exceptions.ConnectionError as e:
            return


def main():
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(connect_google, ip): ip for ip in get_ips()}
        for future in as_completed(futures):
            ip = futures[future]
            code = getattr(future.result(), 'status_code', 'ConnectionError')
            if code != 200:
                print(f'IP {ip} has error {code}')


if __name__ == '__main__':
    main()
