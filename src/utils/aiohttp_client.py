"""Aiohttp client class utility."""
import logging
from socket import AF_INET

import aiohttp
from aiohttp import AsyncResolver

SIZE_POOL_AIOHTTP = 100


class AiohttpClient:
    """Утилита клиента сеанса Aiohttp.
    Служебный класс для обработки асинхронного HTTP-запроса для всей области
    приложения FastAPI.
    """

    def __init__(self, dns_nameservers=None):
        self._log: logging.Logger = logging.getLogger(__name__)

        if dns_nameservers is None:
            dns_nameservers = ["8.8.8.8", "8.8.4.4"]

        resolver = AsyncResolver(nameservers=dns_nameservers)
        self._log.debug("Initialize AiohttpClient session.")
        timeout = aiohttp.ClientTimeout(total=2)
        connector = aiohttp.TCPConnector(
            resolver=resolver,
            family=AF_INET,
            limit_per_host=SIZE_POOL_AIOHTTP,
        )
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
        )

    async def close_session(self):
        """Закрывает сеанс клиента aiohttp."""
        if self._session:
            await self._session.close()

    async def get(self, url: str, headers=None, raise_for_status=False):
        """Выполнить запрос HTTP GET.
         Аргументы:
             url (str): конечная точка запроса HTTP GET.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             response: ответ на запрос HTTP GET — aiohttp.ClientResponse
                 экземпляр объекта.
        """

        self._log.debug(f"Started GET {url}")
        return await self._session.get(
            url,
            headers=headers,
            raise_for_status=raise_for_status,
        )

    async def post(self, url: str, data=None, headers=None, json=None, params=None, raise_for_status=False):
        """Выполнение HTTP POST-запроса.
         Аргументы:
             url (str): конечная точка запроса HTTP POST.
             data (любые): данные для отправки в теле запроса. Это может
                 быть объектом FormData или чем-либо, что может быть передано в
                 Данные формы, например. словарь, байты или файловый объект.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на HTTP-запрос POST — aiohttp.ClientResponse
                 экземпляр объекта.
        """

        self._log.debug(f"Started POST {url}")
        return await self._session.post(
            url,
            data=data,
            headers=headers,
            raise_for_status=raise_for_status,
            json=json,
            params=params,
        )

    async def put(self, url: str, data=None, headers=None, raise_for_status=False):
        """Выполнить HTTP-запрос PUT.
         Аргументы:
             url (str): конечная точка запроса HTTP PUT.
             data (любые): данные для отправки в теле запроса. Это может
                 быть объектом FormData или чем-либо, что может быть передано в
                 Данные формы, например. словарь, байты или файловый объект.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на HTTP-запрос PUT — aiohttp.ClientResponse
                 экземпляр объекта.
        """

        self._log.debug(f"Started PUT {url}")
        return await self._session.put(
            url,
            data=data,
            headers=headers,
            raise_for_status=raise_for_status,
        )

    async def delete(self, url: str, headers=None, raise_for_status=False):
        """Выполнить запрос HTTP DELETE.
         Аргументы:
             url (str): конечная точка HTTP-запроса DELETE.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на запрос HTTP DELETE — aiohttp.ClientResponse
                 экземпляр объекта.
        """

        self._log.debug(f"Started DELETE {url}")
        return await self._session.delete(
            url,
            headers=headers,
            raise_for_status=raise_for_status,
        )

    async def patch(self, url: str, data=None, headers=None, raise_for_status=False):
        """Выполнить запрос HTTP PATCH.
         Аргументы:
             url (str): конечная точка запроса HTTP PATCH.
             data (любые): данные для отправки в теле запроса. Это может
                 быть объектом FormData или чем-либо, что может быть передано в
                 Данные формы, например. словарь, байты или файловый объект.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на запрос HTTP PATCH — aiohttp.ClientResponse
                 экземпляр объекта.
        """

        self._log.debug(f"Started PATCH {url}")
        return await self._session.patch(
            url,
            data=data,
            headers=headers,
            raise_for_status=raise_for_status,
        )