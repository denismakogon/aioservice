# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools

from aiohttp import web


def api_action(**unscoped_kwargs):
    """
    Wrapps API controller action actions handler
    :param unscoped_kwargs: API instance action key-value args
    :return: _api_handler

    Example:

    class Controller(ControllerBase):

        @api_action(method='GET')
        async def index(self, request, **kwargs):
            return web.Response(
                text=str(request),
                reason="dumb API",
                status=201)

    """

    def _api_handler(func):

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, *kwargs)
            except Exception as ex:
                return web.json_response(data={
                    "error": {
                        "message": getattr(ex, "reason", str(ex))
                    }
                }, status=getattr(ex, "status", 500))

        for key, value in unscoped_kwargs.items():
            setattr(wrapper, 'arg_{}'.format(key), value)
        setattr(wrapper, 'is_module_function', True)
        return wrapper

    return _api_handler
