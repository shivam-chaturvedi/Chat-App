# Install all dependencies from requirements.txt (if you create one)
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput
