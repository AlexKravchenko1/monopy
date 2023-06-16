import time
import requests

from typing import List
from datetime import datetime
from errors import Error


class Transaction(object):
    def __init__(self, method: str, path: str):
        self.method = method
        self.endpoint = path
        self.__host = 'https://api.monobank.ua'
        self.__req_headers = {
            '/bank/currency': {"X-Token": ''},
            '/personal/client-info': {"X-Token": ''},
            '/personal/statement': {"X-Token": ''}
        }
        self.__req_paths_params = {
            '/personal/statement': {
                "account": '0',
                "date_from": str(time.mktime(datetime.today().timetuple())),
                "date_to": ''
            }
        }
        self.url = self._create_url()

    @property
    def header(self):
        try:
            return self.__req_headers[self.endpoint]
        except KeyError:
            print(f"Headers does not exist for the path - {self.endpoint}")

    @header.setter
    def header(self, headers: List[str]):
        try:
            token = headers[0]
        except ValueError:
            raise ValueError("Pass an iterable with one item")

        self.__req_headers[self.endpoint]['X-Token'] = token

    @property
    def path_param(self):
        try:
            return self.__req_paths_params[self.endpoint]
        except KeyError:
            print(f"Path parameters does not exist for the path - {self.endpoint}")

    @path_param.setter
    def path_param(self, input_params: List[str]):
        try:
            account, date_from, date_to = input_params
        except ValueError:
            raise ValueError("Pass an iterable with three items")

        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)

        # add to unit test the assertion below
        # assert self.from_datetime <= self.to_datetime, "from_datetime must be less or equal then to_datetime"
        assert date_from <= date_to, "date_from must be less or equal to date_to"

        self.__req_paths_params[self.endpoint].update(
            account=account,
            date_from=str(time.mktime(date_from.timetuple())),
            date_to=str(time.mktime(date_to.timetuple()))
        )

    def _create_url(self):
        if self.endpoint == '/personal/statement':
            url = "/".join(
                ["".join([self.__host, self.endpoint]),
                 self.path_param["account"],
                 self.path_param["date_from"],
                 self.path_param["date_to"]
                 ]
            )
            return url
        else:
            url = "".join([self.__host, self.endpoint])
            return url

    def api_request(self):
        """Handle HTTP requests for monobank endpoints"""
        response = requests.request(self.method, self.url, headers=self.__req_headers[self.endpoint])

        if response.status_code == 200:
            if not response.content:
                return "No content"
            return response.json()
        elif response.status_code == 429:
            raise "Too many requests"

        data = response.json()
        message = data.get("errorDescription", str(data))
        raise Error(message, response)

    def webhook(self):
        pass


class Client(object):
    def __init__(self, private_key: str):
        self.__signature = private_key
        self.__client_info = self._get_client_info()

    def _get_client_info(self):
        """Return client's personal information"""
        transaction = Transaction('GET', "/personal/client-info")
        transaction.header = [self.__signature]
        return transaction.api_request()

    @property
    def client_info(self):
        """This method should be deleted"""
        return self.__client_info

    def get_accounts(self) -> List[str]:
        """Return the list string object with client's account"""
        accounts_list = list()
        for account in self.client_info.get('accounts'):
            accounts_list.append(account)
        return accounts_list

    def get_client_id(self):
        """Return client id"""
        return self.client_info.get('clientId')

    def get_client_name(self):
        """Return client's name"""
        return self.client_info.get('name')

    def get_webhook_url(self):
        """Return client id"""
        return self.client_info.get('webHookUrl')

    def get_personal_statement(self, account: str, dttm_from: str, dttm_to: str = ''):
        """Return client's statements for the specific datetime interval"""
        transaction = Transaction('GET', "/personal/client-info")
        transaction.header = [self.__signature]
        transaction.path_param = [
            account,
            dttm_from,
            dttm_to
        ]
        return transaction.api_request()

    def get_bank_currency(self):
        """Return current bank's currency exchange rate"""
        transaction = Transaction('GET', "/bank/currency")
        transaction.header = [self.__signature]
        return transaction.api_request()
