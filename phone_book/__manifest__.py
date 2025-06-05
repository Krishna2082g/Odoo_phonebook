{
    'name': 'Phone Book',
    'version': '1.0',
    'depends': ['base', 'mail'],  # combined depends here
    'author': 'Krishna',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Manage your contacts in a simple phone book.',
    'description': 'A simple phone book to manage names, phones, emails, and addresses.',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/call_history_views.xml',
        'views/phone_book_views.xml',
        'views/phone_book_invoice_views.xml',
        'views/phone_call_stage_data.xml',
    ],
    'application': True,
    'installable': True,
}
