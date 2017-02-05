#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='lambda-cron',
    version='1.0.0',
    author='MediaMath',
    author_email='jbravo@mediamath.com',
    description='Serverless cron tool to run on AWS',
    keywords='cron lambda aws serverless mediamath',
    url='https://github.com/mediaMath/lambda-cron',
    packages=[
        'lambda_cron', 'lambda_cron.aws', 'lambda_cron.aws.lib', 'lambda_cron.cli'
    ],
    package_dir={'lambda_cron': 'lambda_cron'},
    package_data={'lambda_cron': ['lambda-cron', 'requirements.txt', 'schema.json', 'template.cfn.yml']},
    install_requires=[
        'croniter == 0.3.12',
        'python-dateutil==2.5.3',
        'PyYAML==3.12',
        'requests==2.12.3',
        'jsonschema==2.5.1',
        'boto3==1.4.0'
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