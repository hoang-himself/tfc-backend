sudo -u postgres psql \
  -c "DROP DATABASE tfc;" \
  -c "CREATE DATABASE tfc;" \
  -c "GRANT ALL PRIVILEGES ON DATABASE tfc TO tfc_admin;"

source ./mig-reset.sh