from odoo import fields, models, api
from odoo.exceptions import UserError

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo", domain="[('id', 'in', mp_flujo_ids)]")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", string="Grupo de Flujos")

    @api.onchange("mp_grupo_flujo_id")
    def _onchange_mp_flujo_id(self):
        """ Updates the available flows based on the selected group of flows """
        for register in self:
            register.mp_flujo_id = False  # Reset mp_flujo_id to ensure it's clear before selection
            if register.mp_grupo_flujo_id:
                register.mp_flujo_ids = register.mp_grupo_flujo_id.mp_flujo_ids

    def action_create_payments(self):
        """ Validates the selection of at least one flow or flow group """
        if not self.mp_flujo_id and not self.mp_grupo_flujo_id:
            raise UserError("Debe de tener al menos un flujo o un grupo de flujos seleccionado")
        return super(AccountPaymentRegister, self).action_create_payments()

    def _init_payments(self, to_process, edit_mode=False):
        """ Adds flow data to the payment creation values """
        if to_process and to_process[0] and 'create_vals' in to_process[0]:
            to_process[0]['create_vals'].update({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })
        return super(AccountPaymentRegister, self)._init_payments(to_process, edit_mode)

    def _get_line_batch_key(self, line):
        """ Updates the batch key to include flow details """
        res = super(AccountPaymentRegister, self)._get_line_batch_key(line)
        res.update({
            'mp_flujo_id': line.move_id.mp_flujo_id.id,
            'mp_grupo_flujo_id': line.move_id.mp_grupo_flujo_id.id,
        })
        return res
