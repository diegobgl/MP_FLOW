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
        # Crear los pagos primero sin verificar los valores de flujo y grupo de flujo
        payments = super(AccountPaymentRegister, self)._create_payments()

        # Ahora asignar los valores de Flujo y Grupo de Flujo después de que se han creado los pagos
        for payment in payments:
            if self.mp_flujo_id and self.mp_grupo_flujo_id:
                payment.sudo().write({
                    'mp_flujo_id': self.mp_flujo_id.id,
                    'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id
                })
            else:
                # Si los valores de flujo no están presentes, podrías lanzar una advertencia en lugar de un error
                _logger.warning("No se asignaron los valores de Flujo o Grupo de Flujo para el pago %s", payment.id)
        
        return payments


