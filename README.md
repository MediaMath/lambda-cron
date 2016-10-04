## Local Setup

### Requirments
- Python 2.7
- Virtual Environment
- pip
- Boto3
  - Boto3 is installed as part of the lambda functions Environment.  To aviod the overhead of including it in your deployment artifact install boto3 on your system instead of in the virtual environment
- awscli (configured)

### Setup
From the repo root dir
``` bash
$ virtualenv venv
$ pip install -r requirements.txt
```
