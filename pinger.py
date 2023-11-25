from concurrent.futures import ThreadPoolExecutor
import subprocess
import undetected_chromedriver as uc
import re
import pandas as pd


# generator to yield IPs to be pinged and other data
def scrape(headless=True):
    url = 'https://mullvad.net/en/servers'

    options = uc.ChromeOptions()
    options.headless = headless
    browser = uc.Chrome(options)

    browser.get(url)
    browser.implicitly_wait(10)

    # press some buttons
    wg_button = browser.find_element(
        by='xpath',
        value='//label[.//text()[contains(., "WireGuard")]]'
    )
    wg_button.click()

    online_button = browser.find_element(
        by='xpath',
        value='//label[.//text()[contains(., "Online")]]'
    )
    online_button.click()

    # find number of servers
    div_el = browser.find_element(
        by='xpath',
        value='//div[@data-cy="servers-count"]'
    )
    span_el = div_el.find_element(
        by='xpath',
        value='.//span[1]'
    )
    num_servers = int(span_el.text)

    scrollspace = browser.find_element(by='xpath', value='//div[@class="virtual-scroll-root"]')

    se = set()
    while len(se) < num_servers:
        buttons = scrollspace.find_elements(
            by='xpath',
            value='//div[@class="virtual-scroll-item"]'
        )

        for button in buttons:
            info = button.text.split('\n')
            id = info[0]
            if id in se:
                continue
            else:
                se.add(id)

            country, city, owner = info[1], info[2], info[-1][0]

            button.click()
            tray = button.find_element(by='xpath', value='.//div[@style=""]')

            # highlight_script = "arguments[0].style.border='2px solid red';"
            # browser.execute_script(highlight_script, tray)

            info = tray.find_elements(
                by='xpath',
                value='.//div[@class="dd"]'
            )

            ipv4, socks5, multihop = info[1].text, info[4].text.split(':')[0], info[5].text

            yield {
                'id': id,
                'country': country,
                'city': city,
                'ownership': owner,
                'ipv4': ipv4,
                'socks5': socks5,
                'multihop': multihop
            }

            if headless:  # because of lazy loading
                browser.execute_script(
                    'arguments[0].scrollTop += arguments[1];',
                    scrollspace, button.size['height'] #+ tray.size['height']
                )

    browser.close()
    browser.quit()


def single_ping(address):
    result = subprocess.run(
        f'ping -c 1 {address} ',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    ).stdout

    ip_pattern = r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'
    latency_pattern = r'time=([0-9.]+) ms'

    try:
        ip = re.findall(ip_pattern, result)[0]
        latency = re.findall(latency_pattern, result)[0]
    except IndexError:
        ip, latency = None, None

    return ip, latency


def ping():
    li = []
    addresses = []
    for di in scrape():
        li.append(di)
        addresses.append(di['socks5'])

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(single_ping, addresses))

    new_li = []
    for di, (ip, latency) in zip(li, results):
        if ip and latency:
            di['socks5ip'] = ip
            di['latency'] = latency
            new_li.append(di)

    return pd.DataFrame(new_li)
