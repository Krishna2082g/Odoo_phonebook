import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PhoneBook(models.Model):
    _inherit = 'phone.book'

    def action_create_invoice(self):
        for record in self:
            _logger.info(f"Processing invoice for {record.name} (customer={record.customer})")

            if not record.customer:
                _logger.info(f"Skipping {record.name} as not a customer.")
                continue

            # Get uninvoiced call history lines
            uninvoiced_calls = record.call_history_ids.filtered(lambda c: not c.invoiced)
            if not uninvoiced_calls:
                raise UserError(f"No uninvoiced call history found for {record.name}.")

            # Find or create partner
            partner = self.env['res.partner'].search([('email', '=', record.email)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': record.name,
                    'email': record.email,
                    'phone': record.phone,
                    'street': record.address,
                })

            # Find sales journal
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            if not journal:
                raise UserError("No sales journal found.")

            # Search or create invoice
            invoice = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('partner_id', '=', partner.id),
                ('invoice_origin', '=', record.name),
                ('state', '=', 'draft'),
            ], limit=1)

            if not invoice:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': partner.id,
                    'journal_id': journal.id,
                    'invoice_origin': record.name,
                    'invoice_line_ids': [],
                })
                _logger.info(f"Created new invoice {invoice.name} for {record.name}")
            else:
                _logger.info(f"Updating existing invoice {invoice.name} for {record.name}")

            new_lines = []
            for call in uninvoiced_calls:
                desc = call.call_type.capitalize() if call.call_type else 'Unknown'
                new_lines.append((0, 0, {
                    'name': desc,
                    'quantity': 1,
                    'price_unit': call.total_cost or 0.0,
                }))
                call.invoiced = True  # Mark as invoiced

            invoice.write({'invoice_line_ids': new_lines})
            _logger.info(f"Added {len(new_lines)} new lines to invoice {invoice.name}.")

            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoice.id,
                'target': 'current',
            }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Invoice Creation',
                'message': 'No invoices created or updated.',
                'type': 'warning',
                'sticky': False,
            },
        }
