# -*- coding:utf-8 -*-
# --
# Copyright (c) 2012-2014 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import absolute_import

from . import comp
from kansha.services import Service


class ColumnsService(Service):

    def __init__(self, conf_filename=None, conf=None, error=None,
                 services_service=None):
        self._services = services_service

        super(ColumnsService, self).__init__(conf_filename, conf, error)

    def create_component(self, id_, board, assets_manager, search_engine,
                         data=None):
        return self._services(
            comp.Column, id_, board, assets_manager, search_engine, data
        )
