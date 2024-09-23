from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    mp_flujo_id = fields.Many2one('mp.flujo', string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        
        # Assign 'Flujo' and 'Grupo de Flujo' to journal entries
        for move in self:
            if move.payment_id:
                move.write({
                    'mp_flujo_id': move.payment_id.mp_flujo_id.id,
                    'mp_grupo_flujo_id': move.payment_id.mp_grupo_flujo_id.id,
                })
                
                # Also update the lines
                for line in move.line_ids:
                    line.write({
                        'mp_flujo_id': move.payment_id.mp_flujo_id.id,
                        'mp_grupo_flujo_id': move.payment_id.mp_grupo_flujo_id.id,
                    })

        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mp_flujo_id = fields.Many2one(related='move_id.mp_flujo_id', store=True, string="Flujo")
    mp_grupo_flujo_id = fields.Many2one(related='move_id.mp_grupo_flujo_id', store=True, string="Grupo de Flujo")


