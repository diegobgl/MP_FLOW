from odoo import models, fields, api

class MpGrupoFlujo(models.Model):
    _name = 'mp.grupo.flujo'
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre")
    flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo")

    # Correcting the One2many field without compute and using related for linking
    grupo_flujo_ids = fields.Many2many(
        comodel_name="mp.grupo.flujo", 
        relation="mp_flujo_grupo_rel",  # Asegúrate de que este valor es correcto
        column1="flujo_id",
        column2="grupo_flujo_id"
    )
    mp_flujo_ids = fields.One2many(
        comodel_name="mp.flujo",
        inverse_name="mp_grupo_flujo_id",
        string="Flujos Relacionados"
    )
    flujo_ids = fields.Many2many(
        comodel_name="mp.flujo",
        relation="mp_grupo_flujo_rel",  # Usa un nombre de relación diferente
        column1="grupo_flujo_id",
        column2="flujo_id",
        string="Flujos"
    )
    # Removing compute as it was incorrectly designed for the One2many logic
    # The One2many should rely on the correct inverse relation instead of compute

    # This function can be kept if you need to enforce the linkage explicitly somewhere else
    # but it's not needed for the One2many relationship to work correctly.
    @api.depends('grupo_flujo_ids')
    def _compute_mp_flujo_ids(self):
        for grupo in self:
            grupo.mp_flujo_ids = self.env['mp.flujo'].search([('grupo_flujo_ids', '=', grupo.id)]).ids
