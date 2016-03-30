#--
# Copyright (c) 2012-2014 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from peak import rules
from nagare.i18n import _
from nagare import presentation, security, var, ajax

from .comp import Checklist, ChecklistItem, Checklists, NewChecklistItem


@presentation.render_for(NewChecklistItem)
def render_ChecklistTitle_edit(next_method, self, h, comp, *args):
    """Render the title of the associated object"""
    text = var.Var(u'')
    with h.form(class_='new-item-form'):
        id_ = h.generate_id()
        h << h.input(type='text', value=text, id_=id_, placeholder=_(u'Add item')).action(text)
        h << h.button(_(u'Save'),
                      class_='btn btn-primary').action(lambda: comp.answer(text()))
        h << ' '
        h << h.button(_(u'Cancel'), class_='btn').action(comp.answer)

    if self.focus:
        h << h.script("YAHOO.util.Dom.get(%s).focus()" % ajax.py2js(id_))
        self.focus = False
    return h.root


@presentation.render_for(Checklists, 'action')
def render_Checklists_button(self, h, comp, model):
    if security.has_permissions('checklist', self.card):
        action = ajax.Update(render=lambda r: comp.render(r, model=None),
                             component_to_update='clist' + self.comp_id,
                             action=self.add_checklist)
        with h.a(class_='btn').action(action):
            h << h.i(class_='icon-list')
            h << _('Checklist')
    return h.root


@presentation.render_for(Checklists)
def render_Checklists(self, h, comp, model):
    h.head.javascript_url('checklists/js/checklists.js')
    with h.div(id_='clist' + self.comp_id):
        if security.has_permissions('checklist', self.card):

            # On drag and drop
            action = h.a.action(ajax.Update(action=self.reorder, with_request=True)).get('onclick').replace('return', '')
            action = action.replace('")', '&data="+ YAHOO.lang.JSON.stringify(data))')
            h.head.javascript(h.generate_id(), '''function reorder_checklists(data) {
                %s;
            }''' % action)

            # On items drag and drop
            action = h.a.action(ajax.Update(action=self.reorder_items, with_request=True)).get('onclick').replace('return', '')
            action = action.replace('")', '&data="+ YAHOO.lang.JSON.stringify(data))')
            h.head.javascript(h.generate_id(), '''function reorder_checklists_items(data) {
                    %s;
                }''' % action)

            id_ = h.generate_id()
            with h.div(class_='checklists', id=id_):
                for index, clist in enumerate(self.checklists):
                    h << clist.on_answer(lambda v, index=index: self.delete_checklist(index))
    return h.root


@presentation.render_for(Checklists, 'badge')
def render_Checklists_badge(self, h, comp, model):
    if self.checklists:
        count = ItemsCount()
        count.visit(self)
        with h.span(class_='badge'):
            with h.span(class_='label'):
                h << h.i(class_='icon-list')
                h << ' {} / {}'.format(count.checked, count.total)
    return h.root


@presentation.render_for(Checklist)
def render_Checklist(self, h, comp, model):
    with h.div(id='checklist_%s' % self.id, class_='checklist'):
        with h.div(class_='title'):
            h << h.i(class_='icon-list')
            h << self.title.render(h.AsyncRenderer())
            h << h.a(h.i(class_='icon-cancel'), class_='delete').action(comp.answer, 'delete')

        with h.div(class_='content'):
            if self.items:
                h << comp.render(h, 'progress')
            with h.ul:
                for index, item in enumerate(self.items):
                    h << h.li(item.on_answer(lambda v, index=index: self.delete_index(index)), id='checklist_item_%s' % item().id)
            h << self.new_item
    return h.root


@presentation.render_for(Checklist, 'progress')
def render_Checklist_progress(self, h, comp, model):
    count = ItemsCount()
    count.visit(self)
    progress = count.checked * 100 / count.total
    with h.div(class_='progress progress-success'):
        h << h.div(class_='bar', style='width:%s%%' % progress)
        h << h.span(progress, u'%', class_='percent')
    return h.root


@presentation.render_for(ChecklistItem)
def render_ChecklistItem(self, h, comp, model):
    h << h.a(h.i(class_='icon-checkbox-' + ('checked' if self.done else 'unchecked'))).action(self.set_done)
    h << h.span(self.title.render(h.AsyncRenderer()), class_='done' if self.done else '')
    h << h.a(h.i(class_='icon-cancel'), class_='delete').action(comp.answer, 'delete')
    return h.root


class ItemsCount(object):

    def __init__(self):
        self.total = 0
        self.checked = 0

    @rules.abstract
    def visit(self, element):
        pass

    @rules.when(visit, ChecklistItem)
    def _visit_item(self, item):
        self.total += 1
        if item.done:
            self.checked += 1

    @rules.when(visit, Checklist)
    def _visit_checklist(self, checklist):
        for item in checklist.items:
            self.visit(item())

    @rules.when(visit, Checklists)
    def _visit_checklists(self, checklists):
        for checklist in checklists.checklists:
            self.visit(checklist())
