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

    @api.model
    def default_get(self, fields_list):
        """
        Asegurarse de que los campos de Flujo y Grupo de Flujo se incluyan en los valores predeterminados cuando se
        crea el registro del wizard.
        """
        res = super(AccountPaymentRegister, self).default_get(fields_list)
        # Si los campos están disponibles en el contexto, incluirlos en el wizard
        if 'mp_flujo_id' in self._context:
            res['mp_flujo_id'] = self._context.get('mp_flujo_id')
        if 'mp_grupo_flujo_id' in self._context:
            res['mp_grupo_flujo_id'] = self._context.get('mp_grupo_flujo_id')
        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Asignar los campos de Flujo y Grupo de Flujo a los valores de creación del pago.
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
            'mp_flujo_id': self.mp_flujo_id.id,  # Flujo
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,  # Grupo de Flujo
        }
        return payment_vals

    def action_create_payments(self):
        """
        Heredamos la función action_create_payments para asegurarnos de que los valores de Flujo y Grupo de Flujo
        se asignen correctamente tanto al pago como al asiento contable.
        """
        # Llamamos al método original para crear los pagos
        payments = super(AccountPaymentRegister, self).action_create_payments()

        # Validamos si el resultado es una acción o un conjunto de registros
        if isinstance(payments, dict):
            # Si el resultado es una acción, simplemente la devolvemos
            return payments

        # Si el resultado es un conjunto de registros de pagos, continuamos con la lógica
        for payment in payments:
            if isinstance(payment, models.Model) and payment._name == 'account.payment':  # Asegurarse de que es un registro de pago
                if payment.move_id:  # Verificamos si el asiento contable (move_id) existe
                    move = payment.move_id

                    # Asignamos los valores al asiento en borrador
                    if move.state == 'draft':  # Solo modificar si está en borrador
                        _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable (account.move) en borrador del pago: %s", payment.id)

                        move.sudo().write({
                            'mp_flujo_id': payment.mp_flujo_id.id,
                            'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                        })

                        # Asignamos los valores a las líneas del asiento contable (account.move.line)
                        for move_line in move.line_ids:
                            move_line.sudo().write({
                                'mp_flujo_id': payment.mp_flujo_id.id,
                                'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                            })
                    else:
                        _logger.info("El asiento %s ya está validado, no se puede modificar.", move.name)
                else:
                    _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)
            else:
                _logger.error("La variable payment no es un registro de 'account.payment'. Valor de payment: %s", payment)

        return payments
