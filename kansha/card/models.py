# -*- coding:utf-8 -*-
#--
# Copyright (c) 2012-2014 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from elixir import using_options
from elixir import ManyToMany, ManyToOne, OneToMany, OneToOne
from elixir import Field, Unicode, Integer, DateTime, Date, UnicodeText
from sqlalchemy.orm import subqueryload
from nagare.database import session

from kansha.models import Entity


class DataCard(Entity):

    """Card mapper
    """
    using_options(tablename='card')
    title = Field(UnicodeText)
    description = Field(UnicodeText, default=u'')
    votes = OneToMany('DataVote')
    index = Field(Integer)
    column = ManyToOne('DataColumn')
    labels = ManyToMany('DataLabel')
    comments = OneToMany('DataComment', order_by="-creation_date")
    assets = OneToMany('DataAsset', order_by="-creation_date")
    checklists = OneToMany('DataChecklist', order_by="index")
    members = ManyToMany('DataUser')
    cover = OneToOne('DataAsset', inverse="cover")
    author = ManyToOne('DataUser', inverse="my_cards")
    creation_date = Field(DateTime)
    due_date = Field(Date)
    history = OneToMany('DataHistory')
    weight = Field(Unicode(255), default=u'')

    def delete_history(self):
        for event in self.history:
            session.delete(event)
        session.flush()

    @classmethod
    def delete_card(cls, card):
        """Delete card

        Delete a given card and re-index other cards

        In:
            - ``card`` -- DataCard instance to delete
        """
        index = card.index
        column = card.column
        card.delete()
        session.flush()
        # legacy databases may be broken…
        if index is None:
            return
        q = cls.query
        q = q.filter(cls.index >= index)
        q = q.filter(cls.column == column)
        q.update({'index': cls.index - 1})

    @classmethod
    def get_all(cls):
        query = cls.query.options(subqueryload('labels'), subqueryload('comments'))
        return query

    def make_cover(self, asset):
        """
        """
        DataCard.get(self.id).cover = asset.data

    def remove_cover(self):
        """
        """
        DataCard.get(self.id).cover = None

    def remove_board_member(self, member):
        """Remove member from board"""
        if member.get_user_data() in self.members:
            self.members.remove(member.get_user_data())
            session.flush()
