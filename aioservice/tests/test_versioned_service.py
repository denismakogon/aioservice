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

from aioservice.tests import base


class TestVersionedServiceControllers(base.AIOServiceBase):

    def generate_valid_controller(self, name, c_version):
        class C(controller.ServiceController):
            controller_name = name
            version = c_version

            @requests.api_action(method="GET", route=name)
            async def getter(self, request):
                return web.json_response(data={
                    "name": name
                }, status=200)

        return C

    def test_valid_controllers(self):
        c_name_one, c_name_two = "c-test-one", "c-test-two",
        c_class_one, c_class_two = (
            self.generate_valid_controller(c_name_one, "v1"),
            self.generate_valid_controller(c_name_two, "v1")
        )
        with base.web_service(
                self, versioned_controllers=[
                    c_class_one, c_class_two]) as test_client:
            _, status_1 = self.testloop.run_until_complete(
                test_client.get_some_key("/v1/{}".format(c_name_one)))
            _, status_2 = self.testloop.run_until_complete(
                test_client.get_some_key("/v1/{}".format(c_name_two)))
            self.assertEqual(200, status_1)
            self.assertEqual(200, status_2)

    def test_invalid_controllers(self):
        c_name_one, c_name_two = "c-test-one", "c-test-two",
        c_class_one, c_class_two = (
            self.generate_valid_controller(c_name_one, "v1"),
            self.generate_valid_controller(c_name_two, "v1.5")
        )

        def should_raise():
            with base.web_service(
                    self, versioned_controllers=[
                        c_class_one, c_class_two]):
                pass

        ex = self.assertRaises(Exception, should_raise)
        self.assertIn("not all controllers are pinned "
                      "to the same API version.", str(ex))

    def test_can_create_versioned_service_with_no_controllers(self):
        with base.web_service(self, middleware=[
                base.content_type_validator, ]) as test_client:
            self.assertIsNotNone(test_client)

    def test_can_create_versioned_service_with_no_middleware(self):
        with base.web_service(self, versioned_controllers=[
                self.generate_valid_controller(
                    "test_controller", "v1"), ]) as test_client:
            self.assertIsNotNone(test_client)
