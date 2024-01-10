from pinger import ping
import pandas as pd
import os
import warnings


def generate_list(request_type='file'):
    """
    Generate proxy data.

    Parameters
    ----------
    request_type : {'file', 'df', 'list'}, optional
        Type of request:
            'file': Write proxies to 'proxylist.json', return None.
            'df': Return pandas.DataFrame with proxies.
            'list': Return list of SOCKS5 IPs.

    Returns
    -------
    None, pd.DataFrame, or list
        Depending on the request_type.

    """
    df = ping()

    if request_type == 'df':
        return df
    elif request_type == 'list':
        return df['socks5ip'].tolist()
    elif request_type == 'file':
        script_directory = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_directory, 'proxylist.json')
        df.to_json(output_file, orient='records')
        return
    else:
        raise ValueError("Unsupported request type. Use 'df', 'list', 'file'.")


class ProxyFetcher:
    """
    Abstract class for fetching proxies.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Default: None. Set to None to get a new DataFrame, or pass an existing one.
    update : bool, optional
        Default: False. Set to True to update even if the file exists.

    Methods
    -------
    __init__(df=None, update=False)
        Constructor for ProxyFetcher.

    """
    def __init__(self, df=None, update=False):
        if df:
            self.df = df
        else:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(script_directory, 'proxylist.json')

            if not os.path.exists(output_file) or update:
                generate_list(request_type='file')

            self.df = pd.read_json(output_file)


class RandomProxyFetcher(ProxyFetcher):
    """
    Fetch random proxies from the list.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Default: None. Set to None to get a new DataFrame, or pass an existing one.
    update : bool, optional
        Default: False. Set to True to update even if the file exists.

    Methods
    -------
    __init__(df=None, update=False)
        Constructor for RandomProxyFetcher.

    fetch(**kwargs)
        Returns a single random SOCKS5 IP.

        Parameters
        ----------
        country : str
            Full name of the country (e.g., Italy, UK, USA).
        city : str
            Full name of the city (e.g., Vienna, New York).
        ownership : str
            'O' (Mullvad-owned) or 'R' (rented).
        latency : int
            Maximal tolerated latency.

    fetch_sample(amount=5, **kwargs)
        Returns a sample of random SOCKS5 IPs.

        Parameters
        ----------
        amount : int
            Number of random SOCKS5 IPs to fetch.

    """
    def fetch(self, **kwargs):
        """
        Returns a single random SOCKS5 IP.

        Parameters
        ----------
        country : str
            Full name of the country (e.g., Italy, UK, USA).
        city : str
            Full name of the city (e.g., Vienna, New York).
        ownership : str
            'O' (Mullvad-owned) or 'R' (rented).
        latency : int
            Maximal tolerated latency.

        Returns
        -------
        str
            A single random SOCKS5 IP.

        Raises
        ------
        Exception
            If no proxies with the specified properties are found.

        """
        mask = (
                (self.df['country'] == kwargs.get('country', self.df['country'])) &
                (self.df['city'] == kwargs.get('city', self.df['city'])) &
                (self.df['ownership'] == kwargs.get('owner', self.df['ownership'])) &
                (self.df['latency'] <= kwargs.get('max_latency', self.df['latency']))
        )

        try:
            return self.df[mask].socks5ip.sample().iloc[0]
        except IndexError:
            raise Exception('No proxies with properties found.')

    def fetch_sample(self, amount=5, **kwargs):
        """
        Returns a sample of random SOCKS5 IPs.

        Parameters
        ----------
        amount : int
            Number of random SOCKS5 IPs to fetch.

        Returns
        -------
        list
            A list of random SOCKS5 IPs.

        Warnings
        --------
        - The conditions cannot be met. The program will return an empty list.
        - Sample size was too large; it has been changed to the maximum available.

        """
        mask = (
                (self.df['country'] == kwargs.get('country', self.df['country'])) &
                (self.df['city'] == kwargs.get('city', self.df['city'])) &
                (self.df['ownership'] == kwargs.get('owner', self.df['ownership'])) &
                (self.df['latency'] <= kwargs.get('max_latency', self.df['latency']))
        )

        series = self.df[mask].socks5ip
        size = len(series)

        amount = min(amount, size)

        if size == 0:
            warnings.warn('The conditions cannot be met. The program will return an empty list.', UserWarning)
            return []

        if size < amount:
            warnings.warn(f'Sample size was too large, it has been changed to {amount}.', UserWarning)

        return self.df[mask].socks5ip.sample(n=amount).tolist()
