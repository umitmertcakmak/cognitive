import requests
import json


class ApiClient(object):

    def request(self, method, url, query_params=None, headers=None, body=None, post_params=None):

        """
            :param method: http request method
            :param url: http request url
            :param query_params: query parameters in the url
            :param headers: http request headers
            :param body: request json body, for `application/json`
            :param post_params: request post parameters,
                                `application/x-www-form-urlencode`
                                and `multipart/form-data`
            """

        method = method.upper()
        post_params = post_params or {}
        headers = headers or {}

        if post_params and body:
            raise ValueError(
                "body parameter cannot be used with post_params parameter."
            )

        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        try:
            if method == "POST":
                response = requests.post(url, data=json.dumps(body), headers=headers)
                return response

            if method == "GET":
                response = requests.get(url=url, params=query_params, headers=headers)
                return response

            if method == "PUT":
                response = requests.put(url=url, data=json.dumps(body), params=query_params, headers=headers)
                return response

            if method == "DELETE":
                response = requests.delete(url=url, params=query_params, headers=headers)
                return response

        except requests.exceptions.RequestException as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            raise ApiException(status=0, reason=msg)


class ApiException(Exception):

    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """
        Custom error messages for exception
        """
        error_message = "({0})\n"\
                        "Reason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(self.headers)

        if self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message
