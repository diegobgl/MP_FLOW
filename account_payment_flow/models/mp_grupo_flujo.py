from odoo import models, fields, api

class MpGrupoFlujo(models.Model):
    _name = 'mp.grupo.flujo'
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre")
    flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo")

    # Ajustando la relación para que sea única respecto a otros campos Many2many
    grupo_flujo_ids = fields.Many2many(
        comodel_name="mp.flujo",
        relation="mp_grupo_flujo_grupo_rel",  # Usa un nombre de relación diferente para evitar conflictos
        column1="grupo_flujo_id",
        column2="flujo_id",
        string="Grupos de Flujo"
    )
    
    mp_flujo_ids = fields.One2many(
        comodel_name="mp.flujo",
        inverse_name="mp_grupo_flujo_id",
        string="Flujos Relacionados"
    )

    # Otra relación Many2many con un nombre de tabla único
    flujo_ids = fields.Many2many(
        comodel_name="mp.flujo",
        relation="mp_grupo_flujo_flujo_rel",  # Usa un nombre de relación único
        column1="grupo_flujo_id",
        column2="flujo_id",
        string="Flujos"
    )