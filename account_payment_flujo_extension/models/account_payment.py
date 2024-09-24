from odoo import models, fields
import logging


_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def create(self, vals):
        # Validar que los valores de Flujo y Grupo de Flujo están presentes
        if not vals.get('mp_flujo_id') or not vals.get('mp_grupo_flujo_id'):
            raise ValidationError("Es necesario asignar el Flujo y Grupo de Flujo antes de continuar.")
        return super(AccountPayment, self).create(vals)

    def write(self, vals):
        # Log para verificar la escritura de valores
        _logger.info("Escribiendo valores de Flujo y Grupo de Flujo antes de validar")
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        _logger.info("Ejecutando action_post para el pago con ID: %s", self.id)

        # Validación de que los valores de flujo y grupo de flujo están presentes
        if not self.mp_flujo_id or not self.mp_grupo_flujo_id:
            _logger.warning("Los valores de Flujo o Grupo de Flujo no están asignados en el pago con ID: %s", self.id)
        
        # Lógica principal del asiento
        res = super(AccountPayment, self).action_post()

        # Asignación de los valores al asiento creado
        account_move = self.move_id.sudo()
        account_move.write({
            'mp_flujo_id': self.mp_flujo_id.id,
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
        })

        # Asignación de los valores a las líneas del asiento
        for line in account_move.line_ids:
            line.sudo().write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo", domain="[('id', 'in', mp_flujo_ids)]")
    mp_flujo_ids = fields.One2many(related="mp_grupo_flujo_id.mp_flujo_ids", string="Flujos Relacionados")
