"""``AutoChannel_ui`` lives on
https://github.com/hhollenstain/autochannel-ui
"""
from setuptools import setup, find_packages

INSTALL_REQUIREMENTS = [
    'coloredlogs',
    'Flask',
    'Flask-WTF',
    'flask_bcrypt',
    'flask_bootstrap',
    'flask_sqlalchemy',
    'pip==18.0',
    'pyyaml',
    'requests',
    'requests_oauthlib',
    'waitress',
    'wtforms',
    'WTForms-Alchemy',
]

TEST_REQUIREMENTS = {
    'test':[
        'pytest',
        'pylint',
        'sure',
        ]
    }

setup(
    name='AutoChannel-ui',
    version='0.0.1',
    description='AutoChannel Discord Bot API',
    url='https://github.com/hhollenstain/autochannel-ui',
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIREMENTS,
    extras_require=TEST_REQUIREMENTS,
    entry_points={
        'console_scripts':  [
            'autochannel_ui = run:main',
        ],
    },
    )
