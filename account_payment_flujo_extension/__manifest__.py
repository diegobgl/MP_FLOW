{
    'name': 'Account Payment Flujo Extension',
    'version': '17.0',
    'summary': 'Extension to add mpflujo and mpgrupo_flujo fields to payments',
    'author': 'Your Name',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/account_batch_payment_views.xml',
    
    ],
    'installable': True,
    'application': False,
}
