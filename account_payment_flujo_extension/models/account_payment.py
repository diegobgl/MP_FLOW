from odoo import models, fields
import logging


_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_id = fields.Many2one('mp.flujo', string='Flujo')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    
    def create(self, vals_list):
        """Sobrescribe el método create para asegurarse que Flujo y Grupo de Flujo se asignen correctamente.
        Soporta tanto pagos individuales como múltiples.
        """
        if isinstance(vals_list, list):
            for vals in vals_list:
                if not vals.get('mp_flujo_id') or not vals.get('mp_grupo_flujo_id'):
                    raise ValidationError(_("Es necesario asignar el Flujo y Grupo de Flujo antes de continuar."))
        else:
            if not vals_list.get('mp_flujo_id') or not vals_list.get('mp_grupo_flujo_id'):
                raise ValidationError(_("Es necesario asignar el Flujo y Grupo de Flujo antes de continuar."))

        return super(AccountPayment, self).create(vals_list)

    def write(self, vals):
        """Sobrescribe el método write para asegurarse que Flujo y Grupo de Flujo se escriban correctamente"""
        _logger.info("Escribiendo valores de Flujo y Grupo de Flujo: %s", vals)
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Sobrescribe el método action_post para manejar pagos individuales y asegurar que
        los valores de Flujo y Grupo de Flujo se pasen correctamente al asiento contable creado.
        """
        _logger.info("Ejecutando action_post para el pago con ID: %s", self.id)

        if not self.mp_flujo_id or not self.mp_grupo_flujo_id:
            _logger.warning("Los valores de Flujo o Grupo de Flujo no están asignados en el pago con ID: %s", self.id)

        res = super(AccountPayment, self).action_post()

        for move in self.move_ids:
            move.sudo().write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

            for line in move.line_ids:
                line.sudo().write({
                    'mp_flujo_id': self.mp_flujo_id.id,
                    'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
                })

            _logger.info("Valores escritos en el asiento contable (account.move): Flujo ID: %s, Grupo Flujo ID: %s",
                         self.mp_flujo_id.id, self.mp_grupo_flujo_id.id)

        return res



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")

    def _create_payments(self):
        """ Extiende la lógica para pasar los valores de flujo y grupo de flujo a los pagos creados """
        payments = super(AccountPaymentRegister, self)._create_payments()

        for payment in payments:
            _logger.info("Asignando Flujo y Grupo de Flujo a pago con ID: %s", payment.id)
            payment.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

            account_move = payment.move_id.sudo()
            account_move.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

            for line in account_move.line_ids:
                line.sudo().write({
                    'mp_flujo_id': self.mp_flujo_id.id,
                    'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
                })

        _logger.info("Valores escritos en los pagos múltiples creados correctamente.")
        return payments
