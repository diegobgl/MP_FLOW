from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", domain="[('id', 'in', mp_flujo_ids)]")
    mp_flujo_ids = fields.One2many(related="mp_grupo_flujo_id.mp_flujo_ids")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo")

    @api.onchange("mp_grupo_flujo_id")
    def _onchange_mp_flujo_id(self):
        for register_id in self:
            register_id.mp_flujo_id = self.env['mp.flujo']

    def action_create_payments(self):
        if not self.mp_flujo_id and not self.mp_grupo_flujo_id:
            raise UserError("Debe de tener almenos un flujo o un grupo de flujos seleccionado")
        res = super(AccountPaymentRegister, self).action_create_payments()
        return res

    def _init_payments(self, to_process, edit_mode=False):
        if to_process[0] and to_process[0]['create_vals']:
            to_process[0]['create_vals']['mp_flujo_id'] = self.mp_flujo_id.id
            to_process[0]['create_vals']['mp_grupo_flujo_id'] = self.mp_grupo_flujo_id.id
        res = super(AccountPaymentRegister, self)._init_payments(to_process, edit_mode)
        return res
    
    def _get_line_batch_key(self, line):
        res = super(AccountPaymentRegister, self)._get_line_batch_key(line)
        res.update({
            'mp_flujo_id': line.move_id.mp_flujo_id.id,
            'mp_grupo_flujo_id': line.move_id.mp_grupo_flujo_id.id,
            })
        return res
