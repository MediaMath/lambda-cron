#!/usr/bin/env python

import lambda_cron
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = lambda_cron.__version__

setup(
    name='lambda-cron',
    version=version,
    author='MediaMath',
    author_email='jbravo@mediamath.com',
    description='Serverless cron tool to run on AWS',
    keywords='cron lambda aws serverless mediamath',
    url='https://github.com/mediaMath/lambda-cron',
    download_url='https://github.com/mediamath/lambda-cron/archive/v{0}.tar.gz'.format(version),
    packages=[
        'lambda_cron', 'lambda_cron.aws', 'lambda_cron.aws.lib', 'lambda_cron.cli', 'lambda_cron.cli.command'
    ],
    package_dir={'lambda_cron': 'lambda_cron'},
    package_data={'lambda_cron': ['lambda-cron', 'requirements.txt', 'schema.json', 'template.cfn.yml']},
    install_requires=[
        'croniter>=0.3,<0.4',
        'python-dateutil>=2.5,<2.6',
        'PyYAML>=3.12,<3.13',
        'requests>=2.13,<2.14',
        'jsonschema>=2.6,<2.7',
        'boto3>=1.4,<1.5'
    ],
    entry_points={
        'console_scripts': [
            'lambda-cron=lambda_cron.cli.cli_tool:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ]
)
