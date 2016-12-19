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
import typing

from aiohttp import web

from aioservice.common import logger as log


class VersionedService(object):

    def __init__(self, controllers: typing.List=None,
                 middleware: typing.List=None,
                 service_hooks: typing.List = None):
        self.controllers = controllers if controllers and isinstance(
            controllers, list) else []
        self.middleware = middleware if middleware and isinstance(
            middleware, list) else []
        self.service_hooks = service_hooks if service_hooks and isinstance(
            service_hooks, list) else []

        self.validate_controllers()
        self.validate_middleware()
        self.validate_service_hooks()

    def validate_service_hooks(self):
        if self.service_hooks:
            if not all([callable(hook) for hook in self.service_hooks]):
                raise Exception("All service hooks must be callable.")

    def validate_controllers(self):
        if self.controllers:
            api_version = set([controller.version
                               for controller in self.controllers])
            if len(api_version) != 1:
                raise Exception("Unable to discover common API version "
                                "from controllers, not all controllers "
                                "are pinned to the same API version.")
            return api_version

    def validate_middleware(self):
        if self.middleware:
            all_cors = [asyncio.iscoroutinefunction(middleware)
                        for middleware in self.middleware]
            if len(set(all_cors)) != 1:
                raise Exception("Middleware functions "
                                "should be a coroutines.")

    @property
    def api_version(self):
        if self.validate_controllers():
            api_versions = self.validate_controllers()
            return list(api_versions).pop()

    def bind_to_service(self, service):
        if self.validate_controllers():
            api, controllers = self.api_version, self.controllers
            sub_service_app = web.Application(
                logger=service.logger,
                loop=service.event_loop,
                middlewares=self.middleware)
            for c in controllers:
                c(sub_service_app)
            for hook in self.service_hooks:
                hook(sub_service_app)
            service.root.router.add_subapp(
                "/{}/".format(api), sub_service_app)


class HTTPService(object):

    def __init__(self,
                 subservice_definitions: typing.List,
                 host: str='127.0.0.1',
                 port: int= '10001',
                 event_loop: asyncio.AbstractEventLoop=None,
                 logger=None,
                 debug=False):
        """
        HTTP server abstraction class
        :param host: Bind host
        :param port: Bind port
        :param event_loop: asyncio event-loop
        :param logger: logging.Logger
        """
        self.host = host
        self.port = port
        self.event_loop = event_loop

        if not logger:
            self.logger = log.UnifiedLogger(
                log_to_console=True,
                level="INFO").setup_logger(__package__)
        else:
            self.logger = logger

        self.root = web.Application(
            logger=self.logger,
            loop=self.event_loop,
            debug=debug
        )

        if subservice_definitions and isinstance(
                subservice_definitions, list):
            for subservice_definition in subservice_definitions:
                subservice_definition.bind_to_service(self)

    def apply_swagger(self,
                      swagger_url: str = "/api/doc",
                      description: str = "Swagger API definition",
                      api_version: str = "1.0.0",
                      title: str = "Swagger API",
                      contact: str = ""):
        try:
            import aiohttp_swagger
            aiohttp_swagger.setup_swagger(
                self.root,
                swagger_url=swagger_url,
                description=description,
                api_version=api_version,
                title=title,
                contact=contact,
            )
        except (Exception, ImportError) as ex:
            self.logger.error("Unable to apply swagger. Reason: "
                              "'{}'".format(str(ex)))
        finally:
            return self

    def initialize(self):
        web.run_app(self.root, host=self.host, port=self.port,
                    shutdown_timeout=10, access_log=self.logger)
