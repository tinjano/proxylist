# proxylist
Small project to get SOCKS5 IP addresses of Mullvad proxies.

## How to Use
Use `api.py` with:
```python
from proxylist.api import generate_list, RandomProxyFetcher
```

For example:
```python
proxies = RandomProxyFetcher()

options = uc.ChromeOptions()
options.add_argument(f'--proxy-server=socks5://{proxies.fetch(country="Finland")}')
options.headless = True
browser = uc.Chrome(options)
```

## Dependencies: 
Pandas. Check `requirements.txt`.

## Update Note
The new version uses a CLI command to fetch data that was previously scraped, making
the script much faster.

## Policy
The purpose of this script is getting SOCKS5 IP addresses of Mullvad proxies
and check their availability/latency, a process that would otherwise
have to be manual. Do not use it to act in violation of Mullvad's ToS or principles.
