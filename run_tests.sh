source local_setup.sh
DB_URL=$(python tests/helpers.py url)
DB_NAME=$(python tests/helpers.py name)
dropdb --if-exists $DB_NAME
createdb $DB_NAME
# making this throw away app populates the tables
python -c "from flaskr import create_app;create_app(dburl=\"$DB_URL\")"
python populate_test_db.py $DB_URL
pytest $*
dropdb $DB_NAME
