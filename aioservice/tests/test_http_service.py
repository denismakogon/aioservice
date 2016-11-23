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

from aioservice.tests import base
from aioservice.tests import controllers


class TestHTTPService(base.AIOServiceBase):

    def test_can_do_get_on_service(self):
        with base.web_service(self, versioned_controllers=[
                controllers.TestController], middleware=[
                base.content_type_validator]) as test_client:
            some_key = "some_key"
            json, status = self.testloop.run_until_complete(
                test_client.get_some_key("/v1/{}".format(some_key)))
            self.assertIn(some_key, json)
            self.assertEqual(some_key, json[some_key])
