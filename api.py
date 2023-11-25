from pinger import ping
import json
import pandas as pd
import os
from random import choice, sample
import warnings


# generate a .json file with respective data
def generate_list(request_type='file'):
    """
    request type can be: file, df, list
    file will create a new .json
    df will return data frame
    list will return a list of ips
    """

    df = ping().dropna()

    if request_type == 'df':
        return df
    elif request_type == 'list':
        return df['socks5ip'].tolist()
    elif request_type == 'file':
        script_directory = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_directory, 'proxylist.json')
        df.to_json(
            output_file,
            orient='records',
        )
        return
    else:
        raise Exception('generate_list\'s request type is not supported. Try df, list, file.')


class FetchMullvadProxy:
    """
    init can take a df or it will create it
    it will make a new one if told to do so

    method fetch will return socks5 ip and has kwargs:
        country - which country
        city - which city
        owner - O or R
        max_latency

    method fetch_sample will do same but return
    a list with specified amount of different ips

    """

    def __init__(self, df=None, update=False):
        if df:
            self.df = df
        else:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(script_directory, 'proxylist_another_old.json')

            if not os.path.exists(output_file) or update:
                generate_list(request_type='file')

            self.df = pd.read_json(output_file)

            

    def fetch(self, **kwargs):
        mask = (
                       self.df['country'] == kwargs.get('country', self.df['country'])
               ) & (
                       self.df['city'] == kwargs.get('city', self.df['city'])
               ) & (
                       self.df['ownership'] == kwargs.get('owner', self.df['ownership'])
               ) & (
                       self.df['latency'] <= kwargs.get('max_latency', self.df['latency'])
               )
        try:
            return choice((self.df[mask])['socks5ip'])
        except IndexError:
            raise Exception('No proxies with properties found.')

    def fetch_sample(self, amount=5, **kwargs):
        mask = (
                       self.df['country'] == kwargs.get('country', self.df['country'])
               ) & (
                       self.df['city'] == kwargs.get('city', self.df['city'])
               ) & (
                       self.df['ownership'] == kwargs.get('owner', self.df['ownership'])
               ) & (
                       self.df['latency'] <= kwargs.get('max_latency', self.df['latency'])

               )

        series = self.df[mask]['socks5ip']
        size = len(series)

        amount = min(amount, size)

        if size == 0:
            warnings.warn('The conditions cannot be met. The program will return an empty list.', UserWarning)
            return []

        if size < amount:
            warnings.warn(f'Sample size was too large, it has been changed to {amount}.', UserWarning)

        return sample((self.df[mask])['socks5ip'], amount)


