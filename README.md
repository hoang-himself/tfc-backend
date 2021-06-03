# The Forum Center RESTful API

API/Backend for The Forum Center on Debian

## Clone the repo

- HTTPS

```bash
git clone https://github.com/Smithienious/tfc_backend.git -b development --depth 1
```

- SSH

```bash
git clone git@github.com:Smithienious/tfc_backend.git -b development --depth 1
```

## Change working directory

```bash
cd tfc_backend
```

## (Recommended) Initialize a virtual environment

```bash
python3 -m venv ./venv
source ./venv/bin/activate
```

## Install tools and dependencies

```bash
sudo apt update
sudo apt install -y postgresql
pip install --upgrade pip setuptools wheel pip-tools
pip-sync
```

## (First-time setup) Configure PostgreSQL server

```bash
sudo service postgresql start
sudo -u postgres psql \
-c "CREATE DATABASE tfc;" \
-c "CREATE ROLE tfc_admin WITH ENCRYPTED PASSWORD 'i-am-admin' LOGIN SUPERUSER;" \
-c "GRANT ALL PRIVILEGES ON DATABASE tfc TO tfc_admin;"
python manage.py migrate
python manage.py makemigrations
```

## Running the server

```bash
python manage.py <host>:<port>
```

`<host>` defaults to `127.0.0.1`\
`<port>` defaults to `8000`

## Running tests

`TODO`
