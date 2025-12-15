from . import controllers
from . import models


def create_api_connect_user(env):
    user = env['res.users'].create({
        'name': 'User Amoeba Talk Connector',
        'login': 'amb_talk_connect',
        'email': 'amb_talk_connect',
        'groups_id': [(4, env.ref('base.group_portal').id)],
        'company_id': env.ref('base.main_company').id,
        'company_ids': [(4, env.ref('base.main_company').id)],
    })
    user.generate_api_rest_key()