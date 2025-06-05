from odoo import models, fields

class PhoneCallStage(models.Model):
    _name = 'phone.call.stage'
    _description = 'Phone Call Stage'
    _order = 'sequence'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string="Folded in Kanban")

    # This field is required for your related field in phone.book
    progress = fields.Integer(string="Progress Percent", default=0)
