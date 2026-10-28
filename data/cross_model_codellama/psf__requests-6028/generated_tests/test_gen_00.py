import os
import socket
from urllib.parse import urlparse
import contextlib
import struct


def proxy_bypass(hostname):
    """
    Check if the hostname should bypass the proxy.

    :param hostname: the hostname to check
    :return: True if it should bypass, False otherwise
    """
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    if proxy:
        proxy = urlparse(proxy)
        if proxy.hostname == hostname:
            return True
    return False


def get_environ_proxies(url, no_proxy=None):
    """
    Get the proxies from the environment variables.

    :param url: the URL to check
    :param no_proxy: the no_proxy variable
    :return: the proxies from the environment variables
    """
    proxies = {}
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    if proxy:
        proxies['http'] = proxy
    proxy = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')
    if proxy:
        proxies['https'] = proxy
    if no_proxy:
        proxies['no'] = no_proxy
    return proxies


def should_bypass_proxies(url, no_proxy):
    """
    Check if we should bypass the proxies or not.

    :param url: the URL to check
    :param no_proxy: the no_proxy variable
    :return: True if we should bypass the proxies, False otherwise
    """
    if no_proxy:
        hostname = urlparse(url).hostname
        if hostname:
            if proxy_bypass(hostname):
                return True
    return False


def get_proxies(url, proxies=None, no_proxy=None):
    """
    Get the proxies from the environment variables or the proxies argument.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxies
    """
    if proxies:
        return proxies
    return get_environ_proxies(url, no_proxy)


def proxy_from_url(url, proxies=None, no_proxy=None):
    """
    Get the proxy from the URL or the environment variables.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy
    """
    proxies = get_proxies(url, proxies, no_proxy)
    if proxies:
        return proxies
    return None


def get_proxy_info(url, proxies=None, no_proxy=None):
    """
    Get the proxy information.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy information
    """
    proxy = proxy_from_url(url, proxies, no_proxy)
    if proxy:
        return proxy
    return None


def get_proxy_auth(url, proxies=None, no_proxy=None):
    """
    Get the proxy authentication.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy authentication
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('proxy_auth')
    return None


def get_proxy_headers(url, proxies=None, no_proxy=None):
    """
    Get the proxy headers.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy headers
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('headers')
    return None


def get_proxy_url(url, proxies=None, no_proxy=None):
    """
    Get the proxy URL.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy URL
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('url')
    return None


def should_bypass_proxies(url, no_proxy):
    """
    Check if we should bypass the proxies or not.

    :param url: the URL to check
    :param no_proxy: the no_proxy variable
    :return: True if we should bypass the proxies, False otherwise
    """
    if no_proxy:
        hostname = urlparse(url).hostname
        if hostname:
            if proxy_bypass(hostname):
                return True
    return False


def get_proxies(url, proxies=None, no_proxy=None):
    """
    Get the proxies from the environment variables or the proxies argument.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxies
    """
    if proxies:
        return proxies
    return get_environ_proxies(url, no_proxy)


def proxy_from_url(url, proxies=None, no_proxy=None):
    """
    Get the proxy from the URL or the environment variables.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy
    """
    proxies = get_proxies(url, proxies, no_proxy)
    if proxies:
        return proxies
    return None


def get_proxy_info(url, proxies=None, no_proxy=None):
    """
    Get the proxy information.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy information
    """
    proxy = proxy_from_url(url, proxies, no_proxy)
    if proxy:
        return proxy
    return None


def get_proxy_auth(url, proxies=None, no_proxy=None):
    """
    Get the proxy authentication.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy authentication
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('proxy_auth')
    return None


def get_proxy_headers(url, proxies=None, no_proxy=None):
    """
    Get the proxy headers.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy headers
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('headers')
    return None


def get_proxy_url(url, proxies=None, no_proxy=None):
    """
    Get the proxy URL.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy URL
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('url')
    return None


def get_environ_proxies(url, no_proxy):
    """
    Get the proxies from the environment variables.

    :param url: the URL to check
    :param no_proxy: the no_proxy variable
    :return: the proxies from the environment variables
    """
    proxies = {}
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    if proxy:
        proxies['http'] = proxy
    proxy = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')
    if proxy:
        proxies['https'] = proxy
    if no_proxy:
        proxies['no'] = no_proxy
    return proxies


def proxy_bypass(hostname):
    """
    Check if the hostname should bypass the proxy.

    :param hostname: the hostname to check
    :return: True if it should bypass, False otherwise
    """
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    if proxy:
        proxy = urlparse(proxy)
        if proxy.hostname == hostname:
            return True
    return False


def get_proxy_auth(url, proxies=None, no_proxy=None):
    """
    Get the proxy authentication.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy authentication
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('proxy_auth')
    return None


def get_proxy_headers(url, proxies=None, no_proxy=None):
    """
    Get the proxy headers.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy headers
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('headers')
    return None


def get_proxy_url(url, proxies=None, no_proxy=None):
    """
    Get the proxy URL.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy URL
    """
    proxy = get_proxy_info(url, proxies, no_proxy)
    if proxy:
        return proxy.get('url')
    return None


def get_proxy_info(url, proxies=None, no_proxy=None):
    """
    Get the proxy information.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy information
    """
    if proxies:
        return proxies
    return get_environ_proxies(url, no_proxy)


def get_proxies(url, proxies=None, no_proxy=None):
    """
    Get the proxies from the environment variables or the proxies argument.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxies
    """
    if proxies:
        return proxies
    return get_environ_proxies(url, no_proxy)


def proxy_from_url(url, proxies=None, no_proxy=None):
    """
    Get the proxy from the URL or the environment variables.

    :param url: the URL to check
    :param proxies: the proxies argument
    :param no_proxy: the no_proxy variable
    :return: the proxy
    """
    proxies = get_proxies(url, proxies, no_proxy)
    if proxies:
        return proxies
    return None