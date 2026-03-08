from abc import ABC, abstractmethod
import httpx
import logging
import asyncio


class BaseApiClient(ABC):
    """
    Базовый класс для HTTP клиентов внешних API.

    Включает:
    - Retry логику с exponential backoff
    - Timeout management
    - Логирование
    - Единая обработка ошибок
    """

    def __init__(
            self,
            base_url: str,
            timeout: float = 10.0,
            retries: int = 3,
            backoff: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """Имя клиента для логирования."""
        pass

    def _build_url(self, path: str) -> str:
        """Построить полный URL."""
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def _request(
            self,
            method: str,
            path: str,
            params: dict | None = None,
            json: dict | None = None,
            headers: dict | None = None,
    ) -> dict:
        """Выполнить HTTP запрос с retry логикой."""
        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug(f"{method} {url} params={params} json={json}")

                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.error(f"Timeout after {self.retries} attempts")
                    raise
                wait_time = self.backoff * (2 ** attempt)
                self.logger.warning(f"Timeout, retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                # 5xx ошибки - retry
                if 500 <= e.response.status_code < 600 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2 ** attempt)
                    self.logger.warning(
                        f"Server error {e.response.status_code}, retrying in {wait_time:.2f}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP error: {e}")
                    raise

    async def _get(self, path: str, **kwargs) -> dict:
        """GET запрос."""
        return await self._request("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs) -> dict:
        """POST запрос."""
        return await self._request("POST", path, **kwargs)

    async def close(self) -> None:
        """Закрыть HTTP клиент."""
        await self._client.aclose()
