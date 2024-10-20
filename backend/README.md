# Backend Part of Selita Fish

## Installation

**Database installation**

In `/db`

```bash
docker-compose up -d
```

For more details, see [db/README.md](db/README.md).

**Backend installation**

Create a virtual environment and activate it.

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the requirements.

```bash
pip install -r requirements.txt
```

**Run the backend**

```bash
cd backend   # If you are not in the backend directory
python3 manage.py runserver 0.0.0.0:8080
```
