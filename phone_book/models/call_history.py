from odoo import models, fields, api

class CallHistory(models.Model):
    _name = 'call.history'
    _description = 'Call History'

    contact_id = fields.Many2one('phone.book', string='Contact', required=True, ondelete='cascade')
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)
    invoiced=fields.Boolean(default=False)
    call_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('missed', 'Missed'),
    ], string='Call Type', required=True)

    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)

    @api.depends('start_time', 'end_time', 'contact_id')
    def _compute_total_cost(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = (record.end_time - record.start_time).total_seconds() / 60.0
                record.total_cost = round(duration * 10.0, 2)
            else:
                record.total_cost = 0.0
