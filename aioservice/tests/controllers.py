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

from aiohttp import web

from aioservice.http import controller
from aioservice.http import requests


class TestController(controller.ServiceController):

    controller_name = "test_controllers"
    version = "v1"

    @requests.api_action(method='GET', route="{some_key}")
    async def get_some_(self, request):
        return web.json_response(data={
            "some_key": request.match_info["some_key"]
        }, status=200)
