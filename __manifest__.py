# -*- coding: utf-8 -*-
{
    'name': "gs_crm",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','mail','website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        "data/mail_templates.xml",
        "data/automations.xml",
        'views/res_users_view.xml',
        'views/crm_lead_view.xml',
        'views/login_portal.xml',
        'views/portal_dashboard.xml',
        'data/ir_cron.xml',
        'data/mail_template.xml',
        'views/res_partner_inherit.xml',
    ],

    "installable": True,
    "application": True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

