# -*- coding: utf-8 -*-
{
    'name': "Database Auto Backup Security",
    'summary': 'Make database encrypted when auto backup scheduler run.',
    'description':
        """This module is to use for Database security. By this module database is save
        with password protect zip file. Need password to open and use this database. 
        Decryption message send to authorised person.
        """,
    'author': "Shah Alam Sumon",
    'website': "https://logicbite.wordpress.com/",
    'category': 'Tools',
    'version': '11.0.0.1',
    'installable': True,
    'license': 'LGPL-3',
    'depends': ['auto_backup'],
    'data': [
        'security/db_password_security.xml',
        'wizards/db_password_decrypt_view.xml',
        'views/backup_view.xml',
    ],
    'external_dependencies': {
        "python": ["paramiko", "pyminizip", "cryptography"],
    },
}