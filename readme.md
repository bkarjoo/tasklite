# TaskLite

TaskLite is a lightweight FastAPI-based task management backend with SQLAlchemy and SQLite.

## Setup

1. **Clone the repository:**

   git clone https://github.com/your-username/tasklite.git
   cd tasklite

2. **Install dependencies:**

   pipenv install

3. **Create your `config.py` file (not tracked by Git):**

   Create `tasklite/config.py` with the following content, updating the path as needed:

   DATABASE_PATH = "C:/Users/yourname/My Drive/krow/db/tasklite.db"
   DATABASE_URL = f"sqlite:///{DATABASE_PATH.replace('\\', '/')}"

4. **Run the app:**

   pipenv run uvicorn main:app --reload

## Notes

- `tasklite.db` will be created at the path you define in `config.py`.
- `config.py` is excluded from version control via `.gitignore`.
