from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')


    def _create_payment_entry(self, amount):
        move = super(AccountPayment, self)._create_payment_entry(amount)

        # Heredar los campos `mp_flujo_id` y `mp_grupo_flujo_id` al asiento contable
        move.update({
            'mp_flujo_id': self.mp_flujo_id.id,
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id
        })

        return move


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self, to_process):
        payments = super(AccountPaymentRegister, self)._create_payments(to_process)

        for payment in payments:
            payment.mp_flujo_id = self.mp_flujo_id
            payment.mp_grupo_flujo_id = self.mp_grupo_flujo_id

        return payments
