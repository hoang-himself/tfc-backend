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

cron format helper: https://crontab.guru/

## FAQ

### Generating a password hash

Activate django shell

```bash
python manage.py shell
```

Call the hasher

```python
from django.contrib.auth.hashers import make_password
make_password('sample')
```

### CSRF token

On login, a CSRF token is generated and stored in your cookie.
Take this token, put it in the header and name it `X-CRSFTOKEN`
