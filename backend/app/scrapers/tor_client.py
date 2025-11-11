"""
Tor client for anonymous dark web scraping
"""
import asyncio
import random
from typing import Optional, Dict, Any
import httpx
import socks
import socket
from stem import Signal
from stem.control import Controller
from loguru import logger

from ..core.config import settings


class TorClient:
    """
    Tor client for making anonymous requests to dark web sites
    """

    def __init__(self):
        self.proxy_host = settings.TOR_PROXY_HOST
        self.proxy_port = settings.TOR_PROXY_PORT
        self.control_port = settings.TOR_CONTROL_PORT
        self.password = settings.TOR_PASSWORD
        self.use_tor = settings.USE_TOR

        # Proxy configuration
        self.proxies = None
        if self.use_tor:
            self.proxies = {
                "http://": f"socks5://{self.proxy_host}:{self.proxy_port}",
                "https://": f"socks5://{self.proxy_host}:{self.proxy_port}",
            }

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
        ]

    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.user_agents)

    def renew_tor_circuit(self) -> bool:
        """
        Renew Tor circuit to get a new IP address
        """
        try:
            with Controller.from_port(port=self.control_port) as controller:
                if self.password:
                    controller.authenticate(password=self.password)
                else:
                    controller.authenticate()

                controller.signal(Signal.NEWNYM)
                logger.info("Tor circuit renewed successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to renew Tor circuit: {e}")
            return False

    async def get_tor_session(self) -> Optional[str]:
        """
        Get current Tor session IP address
        """
        try:
            async with httpx.AsyncClient(proxies=self.proxies, timeout=30.0) as client:
                response = await client.get("https://check.torproject.org/api/ip")
                data = response.json()
                ip = data.get("IP", "Unknown")
                is_tor = data.get("IsTor", False)

                if is_tor:
                    logger.info(f"Connected through Tor with IP: {ip}")
                    return ip
                else:
                    logger.warning(f"Not connected through Tor. Current IP: {ip}")
                    return None
        except Exception as e:
            logger.error(f"Failed to check Tor session: {e}")
            return None

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        retries: int = 3,
    ) -> Optional[httpx.Response]:
        """
        Fetch a URL through Tor with retries and error handling

        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            headers: Optional headers
            data: Optional data for POST requests
            timeout: Request timeout in seconds
            retries: Number of retry attempts

        Returns:
            Response object or None if failed
        """
        # Prepare headers
        if headers is None:
            headers = {}

        headers["User-Agent"] = self.get_random_user_agent()

        # Random delay for rate limiting
        delay = random.uniform(settings.SCRAPING_DELAY_MIN, settings.SCRAPING_DELAY_MAX)
        await asyncio.sleep(delay)

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(
                    proxies=self.proxies if self.use_tor else None,
                    timeout=timeout,
                    follow_redirects=True,
                ) as client:

                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    response.raise_for_status()
                    logger.info(f"Successfully fetched: {url}")
                    return response

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {url}: {e}")
                if e.response.status_code in [403, 429]:
                    # Forbidden or rate limited - renew circuit
                    if self.use_tor:
                        self.renew_tor_circuit()
                        await asyncio.sleep(5)
                elif e.response.status_code >= 500:
                    # Server error - retry
                    await asyncio.sleep(2 ** attempt)
                else:
                    # Client error - don't retry
                    return None

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                logger.warning(f"Connection error for {url} (attempt {attempt + 1}/{retries}): {e}")
                if self.use_tor and attempt < retries - 1:
                    self.renew_tor_circuit()
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None

    async def fetch_text(self, url: str, **kwargs) -> Optional[str]:
        """
        Fetch URL and return text content

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for fetch()

        Returns:
            Text content or None
        """
        response = await self.fetch(url, **kwargs)
        return response.text if response else None

    async def fetch_json(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Fetch URL and return JSON data

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for fetch()

        Returns:
            JSON data or None
        """
        response = await self.fetch(url, **kwargs)
        try:
            return response.json() if response else None
        except Exception as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            return None

    def is_onion_url(self, url: str) -> bool:
        """Check if URL is a .onion address"""
        return ".onion" in url.lower()

    def validate_tor_connection(self) -> bool:
        """
        Validate that Tor is running and accessible
        """
        try:
            # Try to connect to Tor SOCKS proxy
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, self.proxy_host, self.proxy_port)
            sock.settimeout(5)
            sock.connect(("check.torproject.org", 80))
            sock.close()
            logger.info("Tor connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Tor validation failed: {e}")
            return False


# Global Tor client instance
tor_client = TorClient()
