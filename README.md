# proxylist
Small project to scrape and try available Mullvad Socks5 proxies.

Use `api.py` with
```
from proxylist.api import generate_list, FetchMullvadProxy
```

see `api.py` for details

Example use:
```
proxies = FetchMullvadProxy()

options = uc.ChromeOptions()
options.add_argument(f'--proxy-server=socks5://{proxies.fetch(country="Finland")}')
options.headless = True
browser = uc.Chrome(options)
```

Dependencies: 
```
pip install pandas undetected-chromedriver
```

Note: Do not use any part of this project in a way that would violate the law or the Terms of Service of Mullvad or some third party.