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

import asyncio
import contextlib
import testtools

from aiohttp import test_utils
from aiohttp import web

from aioservice.http import service


async def content_type_validator(app: web.Application, handler):
    async def middleware_handler(request: web.Request):
        headers = request.headers
        content_type = headers.get("Content-Type")
        if request.has_body:
            if "application/json" != content_type:
                return web.json_response(
                    data={
                        "error": {
                            "message": "Invalid content type"
                        }
                    }, status=400)
        return await handler(request)
    return middleware_handler


class AIOHTTPClient(test_utils.TestClient):

    def __init__(self, http_service):
        super(AIOHTTPClient, self).__init__(http_service)

    async def get_some_key(self, route, headers=None):
        resp = await self.get(route, headers=headers)
        json = await resp.json()
        return json, resp.status


@contextlib.contextmanager
def web_service(test_class_instance,
                versioned_controllers=None,
                middleware=None):

    sub_app = service.VersionedService(
        controllers=versioned_controllers,
        middleware=middleware)

    main_app = service.HTTPService(
        subservice_definitions=[sub_app],
        event_loop=test_class_instance.testloop)

    test_client = AIOHTTPClient(
        main_app.root)

    test_class_instance.testloop.run_until_complete(
        test_client.start_server())
    try:
        yield test_client
    except Exception as ex:
        raise ex
    finally:
        test_class_instance.testloop.run_until_complete(
            test_client.close())


class AIOServiceBase(testtools.TestCase):

    def setUp(self):
        try:
            self.testloop = asyncio.get_event_loop()
        except Exception:
            self.testloop = asyncio.new_event_loop()
            asyncio.set_event_loop(None)

        super(AIOServiceBase, self).setUp()

    def tearDown(self):
        super(AIOServiceBase, self).tearDown()
