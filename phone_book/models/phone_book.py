from odoo import models, fields
from odoo.exceptions import UserError

class PhoneBook(models.Model):
    _name = 'phone.book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Phone Book'

    name = fields.Char(string='Name', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    customer = fields.Boolean(string='Is Customer?', tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    image_1920 = fields.Image()
    color = fields.Integer("Color Index")  # 
    tag_ids = fields.Many2many('res.partner.category', string='Tags', tracking=True)
    
    call_history_ids = fields.One2many('call.history', 'contact_id', string='Call History')

    message_ids = fields.One2many('mail.message', 'res_id', string='Messages', readonly=True)
    message_follower_ids = fields.One2many('mail.followers', 'res_id', string='Followers', readonly=True)

    

    location = fields.Char(string='Location', tracking=True)

    

    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")

    def action_show_map(self):
        self.ensure_one()
        if self.latitude and self.longitude:
            url = f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        

    def action_open_location_map(self):
        self.ensure_one()
        if not self.location:
            raise UserError("No location available.")
        
        query = self.location.replace(' ', '+')
        url = f"https://www.google.com/maps/search/?api=1&query={query}"

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    stage_progress = fields.Integer(
    string='Stage Progress', 
    related='stage_id.progress', 
    store=True, 
    readonly=True
)

    

    stage_id = fields.Many2one(
    'phone.call.stage',
    string='Stage',
    group_expand='_read_group_stage_ids',
    tracking=True
)


    def _read_group_stage_ids(self, stages, domain, order):
        return stages.search([], order=order)



    def action_create_invoice(self):
        self.ensure_one()

        if not self.call_history_ids:
            raise UserError("No call history available to create an invoice.")

        invoice_lines = []
        for call in self.call_history_ids:
            description = (
                f"Customer: {self.name}\n"
                f"Phone: {self.phone}\n"
                f"Email: {self.email}\n"
                f"Address: {self.address}\n"
                f"Call Start: {call.start_time}\n"
                f"Call End: {call.end_time}\n"
                f"Call Type: {call.call_type or 'N/A'}"
            )
            invoice_lines.append((0, 0, {
                'name': description,
                'quantity': 1,
                'price_unit': call.total_cost or 0.0,
            }))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': False,  # Replace with actual partner if available
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
        }

        invoice = self.env['account.move'].create(invoice_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }
    
