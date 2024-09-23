from odoo import models, fields

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    mp_flujo_id = fields.Many2one('mp.flujo', string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mp_flujo_id = fields.Many2one(related='move_id.mp_flujo_id', store=True, string="Flujo")
    mp_grupo_flujo_id = fields.Many2one(related='move_id.mp_grupo_flujo_id', store=True, string="Grupo de Flujo")


