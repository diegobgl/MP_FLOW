from odoo import models, fields

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def action_post(self):
        """Overriding action_post to pass mp_flujo_id and mp_grupo_flujo_id to the account move"""
        _logger.info("Ejecutando action_post para el pago con ID: %s", self.id)
        
        # Log de los valores de flujo y grupo de flujo en el pago
        _logger.info("Valores antes de la validación: Flujo ID: %s, Grupo Flujo ID: %s", self.mp_flujo_id.id, self.mp_grupo_flujo_id.id)

        # Ejecuta el superusuario para asegurar la correcta ejecución
        self.sudo().move_id.write({
            'mp_flujo_id': self.mp_flujo_id.id,
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
        })
        
        # Log después de la asignación
        _logger.info("Valores escritos en el asiento contable (account.move): Flujo ID: %s, Grupo Flujo ID: %s", self.move_id.mp_flujo_id.id, self.move_id.mp_grupo_flujo_id.id)

        # Verificar las líneas del asiento contable
        for line in self.sudo().move_id.line_ids:
            line.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })
            # Log para cada línea
            _logger.info("Valores escritos en la línea del asiento: Flujo ID: %s, Grupo Flujo ID: %s", line.mp_flujo_id.id, line.mp_grupo_flujo_id.id)

        return super(AccountPayment, self).action_post()
