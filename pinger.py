import re
import pandas as pd
import asyncio
import subprocess


def get():
    country_pattern = re.compile(r'(\w+).*')
    city_pattern = re.compile(r'\t([\w\s]+)(?:\(|,).*')
    server_pattern = re.compile(r'\t\t([\w\-]+)\s\(([\d\.]+),\s[\d\w:]+\)'
                                r'\s\-\s(WireGuard|OpenVPN),\shosted\sby\s([^\(]+)\((rented|Mullvad-owned)\)')

    output = subprocess.run(
        'mullvad relay list',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    ).stdout

    country, city = None, None
    for line in output.split('\n'):
        if match := country_pattern.match(line):
            country = match.group(1)
        elif match := city_pattern.match(line):
            city = match.group(1)
        elif match := server_pattern.match(line):
            id_, ip, wg, host, owner = match.groups()

            if wg == 'WireGuard':
                co, ci, wg, nu = id_.split('-')

                yield {
                    'country': country,
                    'city': city,
                    'socks5': f'{co}-{ci}-wg-socks5-{nu}.relays.mullvad.net',
                    'ip': ip,
                    'host': host,
                    'ownership': owner[0].upper()
                }


async def single_ping(address, di):

    process = await asyncio.create_subprocess_shell(
        f'ping -c 1 {address} ',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        text=False
    )

    result, _ = await process.communicate()
    result = result.decode('utf-8')

    ip_pattern = r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'
    latency_pattern = r'time=([0-9.]+) ms'

    try:
        ip = re.findall(ip_pattern, result)[0]
        latency = re.findall(latency_pattern, result)[0]

        di['socks5ip'] = ip
        di['latency'] = latency
    except IndexError:
        pass


async def async_wrapper(addresses, li):
    await asyncio.gather(*[single_ping(address, di) for address, di in zip(addresses, li)])


def ping():
    li = []
    addresses = []

    for di in get():
        li.append(di)
        addresses.append(di['socks5'])

    asyncio.run(async_wrapper(addresses, li))

    return pd.DataFrame([di for di in li if di.get('socks5ip')])
