import os
import socket
import struct
from contextlib import contextmanager
from http.client import InvalidURL
from urllib.error import HTTPError
from urllib.parse import quote, unquote_unreserved, urlparse


def get_environ_proxies(url, no_proxy=None):
    """
    Returns a dictionary with the environment proxies for the given URL.

    :param url: The URL to get the environment proxies for.
    :param no_proxy: The no_proxy environment variable.
    :return: A dictionary with the environment proxies.
    """
    # Prioritize lowercase environment variables over uppercase
    # to keep a consistent behaviour with other http projects (curl, wget).
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())

    # First check whether no_proxy is defined. If it is, check that the URL
    # we're getting isn't in the no_proxy list.
    if no_proxy is None:
        no_proxy = get_proxy('no_proxy')

    parsed = urlparse(url)

    if parsed.hostname is None:
        # URLs don't always have hostnames, e.g. file:/// urls.
        return {}

    if no_proxy:
        # We need to check whether we match here. We need to see if we match
        # the end of the hostname, both with and without the port.
        no_proxy = (
            host for host in no_proxy.replace(' ', '').split(',') if host
        )

        if is_ipv4_address(parsed.hostname):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(parsed.hostname, proxy_ip):
                        return {}
                elif parsed.hostname == proxy_ip:
                    # If no_proxy ip was defined in plain IP notation instead of cidr notation &
                    # matches the IP of the index
                    return {}
        else:
            host_with_port = parsed.hostname
            if parsed.port:
                host_with_port += ':{}'.format(parsed.port)

            for host in no_proxy:
                if parsed.hostname.endswith(host) or host_with_port.endswith(host):
                    # The URL does match something in no_proxy, so we don't want
                    # to apply the proxies on this URL.
                    return {}

    proxy_env_vars = [
        ('http_proxy', get_proxy('http_proxy')),
        ('https_proxy', get_proxy('https_proxy')),
        ('ftp_proxy', get_proxy('ftp_proxy')),
        ('all_proxy', get_proxy('all_proxy')),
    ]

    proxies = {}

    for env_var, proxy in proxy_env_vars:
        if proxy:
            proxies[env_var.split('_')[0]] = proxy

    return proxies


def should_bypass_proxies(url, no_proxy):
    """
    Returns whether we should bypass proxies or not.

    :param url: The URL to check if we should bypass proxies for.
    :param no_proxy: The no_proxy environment variable.
    :return: Whether we should bypass proxies or not.
    """
    # Prioritize lowercase environment variables over uppercase
    # to keep a consistent behaviour with other http projects (curl, wget).
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())

    # First check whether no_proxy is defined. If it is, check that the URL
    # we're getting isn't in the no_proxy list.
    if no_proxy is None:
        no_proxy = get_proxy('no_proxy')

    parsed = urlparse(url)

    if parsed.hostname is None:
        # URLs don't always have hostnames, e.g. file:/// urls.
        return True

    if no_proxy:
        # We need to check whether we match here. We need to see if we match
        # the end of the hostname, both with and without the port.
        no_proxy = (
            host for host in no_proxy.replace(' ', '').split(',') if host
        )

        if is_ipv4_address(parsed.hostname):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(parsed.hostname, proxy_ip):
                        return True
                elif parsed.hostname == proxy_ip:
                    # If no_proxy ip was defined in plain IP notation instead of cidr notation &
                    # matches the IP of the index
                    return True
        else:
            host_with_port = parsed.hostname
            if parsed.port:
                host_with_port += ':{}'.format(parsed.port)

            for host in no_proxy:
                if parsed.hostname.endswith(host) or host_with_port.endswith(host):
                    # The URL does match something in no_proxy, so we don't want
                    # to apply the proxies on this URL.
                    return True

    proxy_env_vars = [
        ('http_proxy', get_proxy('http_proxy')),
        ('https_proxy', get_proxy('https_proxy')),
        ('ftp_proxy', get_proxy('ftp_proxy')),
        ('all_proxy', get_proxy('all_proxy')),
    ]

    for env_var, proxy in proxy_env_vars:
        if proxy:
            if should_bypass_proxies(proxy, no_proxy):
                return True

    return False


def proxy_bypass(url):
    """
    Returns whether we should bypass the proxy or not.

    :param url: The URL to check if we should bypass the proxy for.
    :return: Whether we should bypass the proxy or not.
    """
    parsed = urlparse(url)

    if parsed.hostname is None:
        # URLs don't always have hostnames, e.g. file:/// urls.
        return True

    if is_ipv4_address(parsed.hostname):
        return True

    try:
        with contextlib.closing(socket.socket()) as sock:
            sock.connect((parsed.hostname, parsed.port or 443))
            return True
    except socket.gaierror:
        return True
    except socket.error:
        return False


def get_proxy_dict(proxies=None):
    """
    Returns the proxy dictionary.

    :param proxies: The proxies to use.
    :return: The proxy dictionary.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies


def get_proxy_url(proxies=None):
    """
    Returns the proxy URL.

    :param proxies: The proxies to use.
    :return: The proxy URL.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '')


def proxy_needs_auth(proxies=None):
    """
    Returns whether the proxy needs authentication or not.

    :param proxies: The proxies to use.
    :return: Whether the proxy needs authentication or not.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '').startswith('http://')


def proxy_requires_tls_verification(proxies=None):
    """
    Returns whether the proxy requires TLS verification or not.

    :param proxies: The proxies to use.
    :return: Whether the proxy requires TLS verification or not.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').startswith('http://')


def get_proxy_auth(proxies=None):
    """
    Returns the proxy authentication.

    :param proxies: The proxies to use.
    :return: The proxy authentication.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '').split('@')[1] if proxies.get('http', '').startswith('http://') else None


def get_proxy_username(proxies=None):
    """
    Returns the proxy username.

    :param proxies: The proxies to use.
    :return: The proxy username.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '').split('@')[1].split(':')[0] if proxies.get('http', '').startswith('http://') else None


def get_proxy_password(proxies=None):
    """
    Returns the proxy password.

    :param proxies: The proxies to use.
    :return: The proxy password.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '').split('@')[1].split(':')[1] if proxies.get('http', '').startswith('http://') else None


def get_proxy_ca_certs(proxies=None):
    """
    Returns the proxy CA certs.

    :param proxies: The proxies to use.
    :return: The proxy CA certs.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').split('@')[1].split(':')[1] if proxies.get('https', '').startswith('http://') else None


def get_proxy_key(proxies=None):
    """
    Returns the proxy key.

    :param proxies: The proxies to use.
    :return: The proxy key.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').split('@')[1].split(':')[1] if proxies.get('https', '').startswith('http://') else None


def get_proxy_cert(proxies=None):
    """
    Returns the proxy cert.

    :param proxies: The proxies to use.
    :return: The proxy cert.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').split('@')[1].split(':')[1] if proxies.get('https', '').startswith('http://') else None


def get_proxy_tls_version(proxies=None):
    """
    Returns the proxy TLS version.

    :param proxies: The proxies to use.
    :return: The proxy TLS version.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').split('@')[1].split(':')[1] if proxies.get('https', '').startswith('http://') else None


def get_proxy_ciphers(proxies=None):
    """
    Returns the proxy ciphers.

    :param proxies: The proxies to use.
    :return: The proxy ciphers.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').split('@')[1].split(':')[1] if proxies.get('https', '').startswith('http://') else None


def get_proxy_ca_bundle(proxies=None):
    """
    Returns the proxy CA bundle.

    :param proxies: The proxies to use.
    :return: The proxy CA bundle.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').split('@')[1].split(':')[1] if proxies.get('https', '').startswith('http://') else None


def get_proxy_verify_ssl(proxies=None):
    """
    Returns whether the proxy SSL should be verified or not.

    :param proxies: The proxies to use.
    :return: Whether the proxy SSL should be verified or not.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('https', '').startswith('http://')


def get_proxy_connection_timeout(proxies=None):
    """
    Returns the proxy connection timeout.

    :param proxies: The proxies to use.
    :return: The proxy connection timeout.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '').split('@')[1].split(':')[1] if proxies.get('http', '').startswith('http://') else None


def get_proxy_response_timeout(proxies=None):
    """
    Returns the proxy response timeout.

    :param proxies: The proxies to use.
    :return: The proxy response timeout.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return proxies.get('http', '').split('@')[1].split(':')[1] if proxies.get('http', '').startswith('http://') else None


def get_proxy_url_without_auth(url):
    """
    Returns the proxy URL without authentication.

    :param url: The URL to get the proxy URL without authentication for.
    :return: The proxy URL without authentication.
    """
    parsed = urlparse(url)

    if parsed.hostname is None:
        # URLs don't always have hostnames, e.g. file:/// urls.
        return url

    if is_ipv4_address(parsed.hostname):
        return url

    if proxy_needs_auth():
        return url.replace(proxy_get_auth(), '')

    return url


def get_proxy_auth_header(proxies=None):
    """
    Returns the proxy auth header.

    :param proxies: The proxies to use.
    :return: The proxy auth header.
    """
    if proxies is None:
        proxies = get_environ_proxies('https://example.com')

    return 'Basic {}'.format(base64.b64encode(proxy_get_auth().encode('utf-8')).decode('utf-8')) if proxy_needs_auth() else None


def proxy_get_auth():
    """
    Returns the proxy auth.

    :return: The proxy auth.
    """
    return get_proxy_auth(get_environ_proxies('https://example.com'))


def proxy_get_username():
    """
    Returns the proxy username.

    :return: The proxy username.
    """
    return get_proxy_username(get_environ_proxies('https://example.com'))


def proxy_get_password():
    """
    Returns the proxy password.

    :return: The proxy password.
    """
    return get_proxy_password(get_environ_proxies('https://example.com'))


def proxy_get_ca_certs():
    """
    Returns the proxy CA certs.

    :return: The proxy CA certs.
    """
    return