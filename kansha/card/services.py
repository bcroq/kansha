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

import datetime

from . import comp
from . import models
from kansha.services import Service


class CardsService(Service):

    def __init__(self, conf_filename=None, conf=None, error=None,
                 services_service=None):
        self._services = services_service

        super(CardsService, self).__init__(conf_filename, conf, error)

    def create_component(self, card_id, column, assets_manager, data=None):
        return self._services(comp.Card, card_id, column, assets_manager, data)

    def create_card(self, column, title, user):
        """Create new card data

        In:
            - ``column`` -- DataColumn, father of the column
            - ``title`` -- title of the card
            - ``user`` -- DataUser, author of the card
        Return:
            - created DataCard instance
        """
        card = models.DataCard(
            title=title,
            author=user,
            creation_date=datetime.datetime.utcnow()
        )
        column.cards.append(card)
        return card
