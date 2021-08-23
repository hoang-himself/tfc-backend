# The Forum Center Backend

## Clone the repo

- HTTPS

```bash
git clone https://github.com/Smithienious/tfc-backend.git -b develop --depth 1
```

- SSH

```bash
git clone git@github.com:Smithienious/tfc-backend.git -b develop --depth 1
```

## Change working directory

```bash
cd tfc-backend
```

## (Recommended) Initialize a virtual environment

```bash
python -m venv --upgrade-deps ./.venv
source ./.venv/bin/activate
```

## Install tools and dependencies

```bash
sudo apt update
sudo apt install -y postgresql
pip install pip-tools
pip-sync
```

## First-time setup

### Configure PostgreSQL server

```bash
sudo service postgresql start
sudo -u postgres psql \
-c "CREATE DATABASE tfc;" \
-c "CREATE ROLE tfc_admin WITH ENCRYPTED PASSWORD 'i-am-admin' LOGIN SUPERUSER;" \
-c "GRANT ALL PRIVILEGES ON DATABASE tfc TO tfc_admin;"
```

### Migrate the database

```bash
python manage.py makemigrations
python manage.py makemigrations master_db
python manage.py migrate
```

## Running the server

```bash
python manage.py <host>:<port>
```

`<host>` defaults to `127.0.0.1`\
`<port>` defaults to `8000`

## WSL Cron

Activating Cron

```bash
sudo usermod -a -G crontab <username>
sudo service cron
service cron status
```

First time running cron

```bash
crontab -e
```

Content needed for crontab -e

```sh
SHELL=/bin/bash
*/3 * * * * . /<project-location>/venv/bin/activate && python /<project-location>/manage.py
```

cron format helper: [Link](https://crontab.guru/)

## FAQ

### JWT token

On login, a JWT token is returned in the response body.
Take this token, put it in the header according to this format

```text
'Authorization': 'JWT <token>'
```

The space behind `JWT` is important.

### SECRET_KEY and JWT_KEY

By default, this program reads the keys from shell environment variables, i.e. `export SECRET_KEY=<key>`

You can generate the keys using the Django shell at `python manage.py shell`

```python
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
```

### Logout

Currently not implemented.
Clients are required to delete any JWT token saved.

## Utility functions

### Clear database

```bash
sudo -u postgres psql \
  -c "DROP DATABASE tfc;" \
  -c "CREATE DATABASE tfc;" \
  -c "GRANT ALL PRIVILEGES ON DATABASE tfc TO tfc_admin;"
```

### Clean cache and migrations file, with creating default superuser

```bash
find . -type f -name "*.py[co]" -delete
find . -type d -name "__pycache__" -delete
find . -depth -type d -name ".mypy_cache" -exec rm -r {} +
find . -depth -type d -name ".pytest_cache" -exec rm -r {} +
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/db/*" -delete

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

python manage.py createsuperuser_with_password \
--email 'owner@localhost.com' \
--mobile '0999999999' \
--password 'iamowner' \
--preserve --no-input
```

## TODO

- Authorization
