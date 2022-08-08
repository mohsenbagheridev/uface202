# -*- coding: utf-8 -*-
# from odoo import http


# class MbUface202(http.Controller):
#     @http.route('/mb_uface202/mb_uface202/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mb_uface202/mb_uface202/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mb_uface202.listing', {
#             'root': '/mb_uface202/mb_uface202',
#             'objects': http.request.env['mb_uface202.mb_uface202'].search([]),
#         })

#     @http.route('/mb_uface202/mb_uface202/objects/<model("mb_uface202.mb_uface202"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mb_uface202.object', {
#             'object': obj
#         })
