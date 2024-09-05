from odoo import models, fields, api

class MpGrupoFlujo(models.Model):
    _name = 'mp.grupo.flujo'
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre")
    flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo")

    # Many2many with a unique relation name to avoid conflicts
    grupo_flujo_ids = fields.Many2many(
        comodel_name="mp.flujo",  # Ajustado para reflejar correctamente la relación
        relation="mp_flujo_grupo_rel",  # Asegúrate de que este valor es único y no usado en otro campo
        column1="flujo_id",
        column2="grupo_flujo_id",
        string="Grupos de Flujo"
    )

    # Correct One2many field definition
    mp_flujo_ids = fields.One2many(
        comodel_name="mp.flujo",
        inverse_name="mp_grupo_flujo_id",
        string="Flujos Relacionados"
    )

    # Many2many field with a different relation to avoid conflict with the other Many2many field
    flujo_ids = fields.Many2many(
        comodel_name="mp.flujo",
        relation="mp_grupo_flujo_flujo_rel",  # Usa un nombre de relación diferente para evitar conflictos
        column1="grupo_flujo_id",
        column2="flujo_id",
        string="Flujos"
    )

    # The compute method was removed as it was not correctly designed for the One2many logic
    # One2many fields should directly rely on the inverse relation.
