from odoo import models, fields, api, _
from odoo.exceptions import ValidationError  # Importar ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_id = fields.Many2one('mp.flujo', string='Flujo')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    @api.model
    def create(self, vals_list):
        """Sobrescribe el método create para asegurarse que Flujo y Grupo de Flujo se asignen correctamente.
        Soporta tanto pagos individuales como múltiples.
        """
        return super(AccountPayment, self).create(vals_list)

    def write(self, vals):
        """Sobrescribe el método write para asegurarse que Flujo y Grupo de Flujo se escriban correctamente"""
        _logger.info("Escribiendo valores de Flujo y Grupo de Flujo: %s", vals)
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Sobreescribe el método action_post para asignar los valores de Flujo y Grupo de Flujo a los asientos contables."""
        # Llamada al método original de Odoo para procesar el pago
        res = super(AccountPayment, self).action_post()

        # Asignar los valores de Flujo y Grupo de Flujo a los asientos contables y sus líneas
        for payment in self:
            if payment.move_id:  # Asegúrate de que el asiento contable (move_id) existe
                _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable (account.move) del pago: %s", payment.id)
                payment.move_id.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })
                
                # Ahora también asignamos a las líneas del asiento contable (account.move.line)
                for move_line in payment.move_id.line_ids:
                    _logger.info("Asignando Flujo y Grupo de Flujo a las líneas del asiento contable (account.move.line): %s", move_line.id)
                    move_line.sudo().write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
            else:
                _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)

        return res



_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Sobreescribimos este método para incluir los campos de Flujo y Grupo de Flujo en los valores de creación del pago.
        """
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'write_off_line_vals': [],
            'mp_flujo_id': self.mp_flujo_id.id,  # Añadir Flujo
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,  # Añadir Grupo de Flujo
        }

        return payment_vals

    def _create_payments(self):
        """
        Sobreescribimos la función para asignar valores de Flujo y Grupo de Flujo a los asientos contables y sus líneas
        Si el asiento está validado, volver a borrador, asignar valores y validar nuevamente.
        """
        # Llamar al método original para crear los pagos (esto también crea los asientos en borrador)
        payments = super(AccountPaymentRegister, self)._create_payments()

        # Asignar los valores de Flujo y Grupo de Flujo a los asientos contables
        for payment in payments:
            if payment.move_id:  # Verifica si el asiento contable (move_id) existe
                move = payment.move_id
                
                # Si el asiento está validado, ponerlo en borrador primero
                if move.state == 'posted':
                    _logger.info("El asiento %s está validado. Se establecerá en borrador antes de asignar los valores.", move.name)
                    move.button_draft()  # Cambia el estado del asiento a borrador
                
                # Asignar Flujo y Grupo de Flujo al asiento contable (account.move)
                _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable (account.move) en borrador del pago: %s", payment.id)
                move.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })
                
                # Asignar Flujo y Grupo de Flujo a las líneas del asiento contable (account.move.line)
                for move_line in move.line_ids:
                    move_line.sudo().write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
                
                # Validar nuevamente el asiento
                _logger.info("Validando nuevamente el asiento contable (account.move): %s", move.name)
                move.action_post()
            else:
                _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)

        return payments
