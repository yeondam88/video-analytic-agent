## SpecStory

## FastAPI Server Error Troubleshooting (2/15/2025, 8:57:49 PM)

_**User**_

We are getting a lot of errors in the console when we are trying to run our fast api server

---

_**Assistant**_

I'll help investigate the errors in the FastAPI server. First, let me check the current state of the codebase and any error messages.

---

_****_

```bash
source venv/bin/activate && python -m uvicorn src.api.main:app --reload 2>&1 | cat
```

```
INFO:     Will watch for changes in these directories: ['/Users/yeondampark/code
s/superdisco/video-analytic-
agent']
                            ERROR:    [Errno 48] Address already in use

```

---

_****_



I see that there's an issue with the port being already in use. Let me first check if there's any running uvicorn process and then look at the server code for potential issues.

---

_****_

```bash
ps aux | grep uvicorn | cat
```

```
(venv) (venv) yeondampark@Mac video-analytic-agent % ps aux | grep uvicorn | cat
yeondampark      86530  34.0  0.1 411741568  39712 s034  R+    8:54PM   2:09.77 /Users/yeondampark/codes/sup
erdisco/video-analytic-agent/venv/bin/python3 /Users/yeondampark/codes/superdisco/video-analytic-agent/venv/
bin/uvicorn src.api.main:app --reload --port 8000
yeondampark      87761   0.0  0.0 410210080   1376 s036  S+    8:58PM   0:00.00 grep uvicorn
(venv) (venv) yeondampark@Mac video-analytic-agent %
```

---

_****_



I see that there's already a uvicorn process running. Let's kill it and then check the FastAPI server code for any potential issues.

---

_****_

```bash
kill 86530 && sleep 2
```

```
(venv) (venv) yeondampark@Mac video-analytic-agent % 

```

---

_****_



Now let me check the FastAPI server code to see if there are any issues.

---

_****_

<details>
            <summary>Searched codebase "FastAPI app initialization and configuration" • **25** results</summary>
        
| File | Lines |
|------|-------|
| `src/api/main.py` | L1-41 |
| `src/api/core/config.py` | L1-44 |
| `src/api/config/settings/__init__.py` | L1-20 |
| `src/api/config/settings/api.py` | L1-64 |
| `src/api/config/settings/database.py` | L1-56 |
| `src/api/config/settings.py` | L106-158 |
| `src/api/app.py` | L1-32 |
| `src/api/database.py` | L45-101 |
| `src/api/config/settings.py` | L1-43 |
| `src/api/config/settings/paths.py` | L1-40 |
| `src/api/config/settings/services.py` | L1-58 |
| `src/api/core/config.py` | L59-97 |
| `src/api/config/settings.py` | L43-106 |
| `src/api/config/settings/__init__.py` | L20-30 |
| `src/api/routers/base.py` | L60-74 |
| `src/api/config/settings/base.py` | L1-18 |
| `src/api/database/manager.py` | L47-103 |
| `src/api/config/settings/database.py` | L56-88 |
| `src/api/core/database.py` | L1-41 |
| `src/api/config/settings.py` | L158-207 |
| `src/api/config/settings/paths.py` | L40-90 |
| `src/api/core/config.py` | L44-59 |
| `src/api/config/settings/database.py` | L88-123 |
| `src/api/middleware/rate_limiter.py` | L1-42 |
| `src/api/config/settings.py` | L207-258 |

</details>

---

_****_



Let me check the `.env` file to see if all required environment variables are properly set.

---

_****_

Read file: .env

---

_****_



Now let me check if the required directories exist and have proper permissions.

---

_****_

```bash
ls -la storage/
```

```
(venv) (venv) yeondampark@Mac video-analytic-agent % ls -la storage/
total 0
drwxr-xr-x@  4 yeondampark  staff  128 Feb 14 15:07 .
drwxr-xr-x@ 31 yeondampark  staff  992 Feb 15 20:40 ..
drwxr-xr-x@  2 yeondampark  staff   64 Feb 14 15:07 audio
drwxr-xr-x@  2 yeondampark  staff   64 Feb 14 15:07 videos
(venv) (venv) yeondampark@Mac video-analytic-agent %
```

---

_****_



The storage directories exist and have proper permissions. Let me check if the database is accessible.

---

_****_

```bash
python3 -c "from src.db.database import db; import asyncio; asyncio.run(db.list('videos', limit=1))" 2>&1 | cat
```

```
< asyncio.run(db.list('videos', limit=1))" 2>&1 | cat
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/database.py", line 11, in <module>
    from src.api.core.database import db_settings
  File "/Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/core/database.py", line 45, in <mod
ule>
    db_settings = DatabaseSettings() 
                  ^^^^^^^^^^^^^^^^^^
  File "/Users/yeondampark/codes/superdisco/video-analytic-agent/venv/lib/python3.11/site-packages/pydantic_
settings/main.py", line 171, in __init__
    super().__init__(
  File "/Users/yeondampark/codes/superdisco/video-analytic-agent/venv/lib/python3.11/site-packages/pydantic/
main.py", line 214, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 3 validation errors for DatabaseSettings
DB_HOST
  Field required [type=missing, input_value={'SUPABASE_URL': 'https:/...DIR': './storage/audio'}, input_type
=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
DB_USER
  Field required [type=missing, input_value={'SUPABASE_URL': 'https:/...DIR': './storage/audio'}, input_type
=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
DB_PASSWORD
  Field required [type=missing, input_value={'SUPABASE_URL': 'https:/...DIR': './storage/audio'}, input_type
=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
(venv) (venv) yeondampark@Mac video-analytic-agent %
```

---

_****_





I see the issue. There's a mismatch between the environment variable names in the `.env` file and what the application is expecting. Let me fix this by editing the database settings.

---

_****_



---

_****_



I apologize for the confusion. Let me try a different approach. Let's check the database module to see how it's being used.

---

_****_

Read file: src/db/database.py

---

_****_





I see the issue now. The database module is trying to use both the settings from `config.settings` and `src.api.core.database`. Let me fix this by consolidating the database settings.

---

_****_

```diff
  
  from config.settings import settings
- from src.api.core.database import db_settings
  
  
                  # Create SQLAlchemy engine with connection pooling
                  self._engine = create_engine(
-                     str(db_settings.DATABASE_URL),
+                     settings.get_sqlalchemy_url(),
                      poolclass=QueuePool,
-                     pool_size=db_settings.DB_POOL_SIZE,
-                     max_overflow=db_settings.DB_MAX_OVERFLOW,
-                     pool_timeout=db_settings.DB_POOL_TIMEOUT,
+                     pool_size=5,
+                     max_overflow=10,
+                     pool_timeout=30,
                      pool_pre_ping=True,
                      pool_recycle=1800,  # Recycle connections after 30 minutes
```

---

_****_





Now let's try running the FastAPI server again.

---

_****_

```bash
source venv/bin/activate && python -m uvicorn src.api.main:app --reload 2>&1 | cat
```

```
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: maximum recursion depth exceeded while calling a Python object 
[type=value_error, input_value=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSett
ings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue={'DATABASE_URL': 'postgre...dir': './storage/audio'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error
```

---

_****_





I see the issue. There's a recursive validation error in the database settings. Let me fix the database settings class.

---

_****_

```diff
      
      # Connection settings
-     DB_HOST: str = Field(..., env="SUPABASE_DB_HOST")
-     DB_PORT: int = Field(5432, env="SUPABASE_DB_PORT")
-     DB_NAME: str = Field("postgres", env="SUPABASE_DB_NAME")
-     DB_USER: str = Field(..., env="SUPABASE_DB_USER")
-     DB_PASSWORD: str = Field(..., env="SUPABASE_DB_PASSWORD")
+     DB_HOST: str = Field(default="localhost", env="SUPABASE_DB_HOST")
+     DB_PORT: int = Field(default=5432, env="SUPABASE_DB_PORT")
+     DB_NAME: str = Field(default="postgres", env="SUPABASE_DB_NAME")
+     DB_USER: str = Field(default="postgres", env="SUPABASE_DB_USER")
+     DB_PASSWORD: str = Field(default="postgres", env="SUPABASE_DB_PASSWORD")
      
      # Connection pool settings
-     DB_POOL_SIZE: int = Field(10, env="DB_POOL_SIZE")
-     DB_MAX_OVERFLOW: int = Field(20, env="DB_MAX_OVERFLOW")
-     DB_POOL_TIMEOUT: int = Field(30, env="DB_POOL_TIMEOUT")
+     DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
+     DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
+     DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
      
      # SSL settings
-     DB_SSL_MODE: str = Field("require", env="DB_SSL_MODE")
+     DB_SSL_MODE: str = Field(default="require", env="DB_SSL_MODE")
      
      model_config = SettingsConfigDict(
      )
      
-     @property
-     def DATABASE_URL(self) -> PostgresDsn:
-         """Construct database URL from components."""
-         return PostgresDsn.build(
-             scheme="postgresql+psycopg2",
-             username=self.DB_USER,
-             password=self.DB_PASSWORD,
-             host=self.DB_HOST,
-             port=self.DB_PORT,
-             path=f"/{self.DB_NAME}",
-             query={"sslmode": self.DB_SSL_MODE}
-         )
+     def get_database_url(self) -> str:
+         """Get the database URL."""
+         return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSL_MODE}"
  
  
```

---

_****_





Now I need to update the database module to use the new method.

---

_****_

```diff
  
  from config.settings import settings
+ from src.api.core.database import DatabaseSettings
  
+ # Initialize database settings
+ db_settings = DatabaseSettings()
  
  class Database:
                  # Create SQLAlchemy engine with connection pooling
                  self._engine = create_engine(
-                     settings.get_sqlalchemy_url(),
+                     db_settings.get_database_url(),
                      poolclass=QueuePool,
-                     pool_size=5,
-                     max_overflow=10,
-                     pool_timeout=30,
+                     pool_size=db_settings.DB_POOL_SIZE,
+                     max_overflow=db_settings.DB_MAX_OVERFLOW,
+                     pool_timeout=db_settings.DB_POOL_TIMEOUT,
                      pool_pre_ping=True,
                      pool_recycle=1800,  # Recycle connections after 30 minutes
```

---

_****_







Now let's try running the FastAPI server again.

---

_****_

```bash
source venv/bin/activate && python -m uvicorn src.api.main:app --reload 2>&1 | cat
```

```
(venv) (venv) yeondampark@Mac video-analytic-agent % 
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: 1 validation error for DatabaseSettings
  Value error, Failed to parse DATABASE_URL: maximum recursion depth exceeded while calling a Python object 
[type=value_error, input_value=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSett
ings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue=DatabaseSettings(DATABASE...=10, DB_POOL_TIMEOUT=30), input_type=DatabaseSettings]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error [type=value_error, input_va
lue={'DATABASE_URL': 'postgre...dir': './storage/audio'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/value_error
^C
^C
^C


```

---

_****_



I see that the command was interrupted. Let me try again with a different port.

---

_****_

```bash
source venv/bin/activate && python -m uvicorn src.api.main:app --reload --port 8001 2>&1 | cat
```

```
    For further information visit https://errors.pydantic.dev/2.10/v/value_error
```

---

_****_





I see that we're still getting validation errors. Let me check the main FastAPI application code.

---

_****_

Read file: src/api/main.py

---

_****_





I see that we're importing `db` from `src.api.database`, but we moved the database module to `src.db.database`. Let me fix this import.

---

_****_

```diff
  
  from src.api.routers import videos, summaries, search
- from src.api.database import db
+ from src.db.database import db
  
  app = FastAPI(
```

---

_****_







Now let's try running the FastAPI server again.

---

_****_



---

_****_





I apologize for the confusion. Let me check if there are any other issues with the imports.

---

_****_



---

_****_





Let me try a different search.

---

_****_

<details>
            <summary>Grep search for "from.*database import" • **24** files</summary>
        
| File | Line | Match |
|------|------|-------|
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/main.py` | L5 | `from src.api.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/app.py` | L6 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/test_db_connection.py` | L24 | `from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/dependencies/services.py` | L7 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/routers/videos.py` | L7 | `from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/routers/videos.py` | L13 | `from ..dependencies.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/config/settings/__init__.py` | L6 | `from .database import DatabaseSettings` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/utils/setup_db.py` | L4 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/database.py` | L10 | `from src.api.core.database import DatabaseSettings` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/routers/search.py` | L4 | `from src.api.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/routers/summaries.py` | L4 | `from ..database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/utils/test_connection.py` | L7 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/transcription/transcriber.py` | L8 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/audio/extractor.py` | L9 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/coordinator.py` | L8 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/segmentation/processor.py` | L9 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/video/downloader.py` | L9 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/tests/test_pipeline.py` | L8 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/test_imports.py` | L3 | `from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/tests/integration/test_database.py` | L5 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/comprehensive-guide-for-fastapi-and-supabase-connection.md` | L170 | `from src.api.config.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/comprehensive-guide-for-fastapi-and-supabase-connection.md` | L455 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/supabase-database-connection-troubleshooting.md` | L872 | `from src.api.config.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L819 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L1722 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L2255 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L2952 | `+ from ..dependencies.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L3961 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4146 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4313 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4413 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4582 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4619 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4656 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4693 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4730 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L5237 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L5523 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L5937 | `+ from src.api.core.database import db_settings` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/fastapi-and-supabase-connection-troubleshooting.md` | L15569 | `from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1224 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1315 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1404 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1513 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1719 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1818 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L3150 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L3298 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L3487 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L6953 | `+ from database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L7015 | `+ from database import Base, engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L12350 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L12416 | `+ from src.api.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L12511 | `from database import Base, engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13311 | `- from database import Base, engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13314 | `+ from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13568 | `+ from ..database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13615 | `- from database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13616 | `+ from ..database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13661 | `from src.api.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13982 | `from ..database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L14386 | `+ from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L18463 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L18679 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L19297 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20186 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20304 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20789 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20836 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L23914 | `+ from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L25248 | `- from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26638 | `- from ..database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26640 | `+ from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26811 | `- from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26815 | `+ from src.api.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L33434 | `+ from .database import DatabaseSettings` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L33840 | `+ from src.api.database import db, DatabaseError` |

</details>

---

_****_







I see that there are several files still using the old database import path. Let me fix them.

---

_****_



---

_****_





Let me try a different approach. Let me check if the file exists first.

---

_****_

<details>
            <summary>Listed directory src/api/routers • **5** results</summary>
        
| Name |
|-------|
| 📄 `__pycache__` |
| 📄 `videos.py` |
| 📄 `base.py` |
| 📄 `summaries.py` |
| 📄 `search.py` |

</details>

---

_****_







Now let me read the current content of the videos.py file.

---

_****_

Read file: src/api/routers/videos.py

---

_****_







I see the issue. The videos.py file is importing from multiple database modules. Let me fix this.

---

_****_



---

_****_







Let me try a different approach. Let me check if there are any other files that need to be fixed.

---

_****_

Read file: src/api/routers/search.py

---

_****_







Let me check the summaries.py file as well.

---

_****_

Read file: src/api/routers/summaries.py

---

_****_









I see that we need to fix the database imports in multiple files. Let me create a new database module that will handle both SQLAlchemy and Supabase connections.

---

_****_



---

_****_







Let me try a different approach. Let me check if we have any circular dependencies.

---

_****_

<details>
            <summary>Grep search for "from.*src.*database.*import" • **22** files</summary>
        
| File | Line | Match |
|------|------|-------|
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/main.py` | L5 | `from src.api.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/app.py` | L6 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/test_db_connection.py` | L24 | `from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/dependencies/services.py` | L7 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/routers/search.py` | L4 | `from src.api.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/api/routers/videos.py` | L7 | `from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/audio/extractor.py` | L9 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/utils/setup_db.py` | L4 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/segmentation/processor.py` | L9 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/coordinator.py` | L8 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/video/downloader.py` | L9 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/database.py` | L10 | `from src.api.core.database import DatabaseSettings` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/pipeline/transcription/transcriber.py` | L8 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/src/db/utils/test_connection.py` | L7 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/test_imports.py` | L3 | `from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/tests/test_pipeline.py` | L8 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/tests/integration/test_database.py` | L5 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/comprehensive-guide-for-fastapi-and-supabase-connection.md` | L170 | `from src.api.config.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/comprehensive-guide-for-fastapi-and-supabase-connection.md` | L455 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/supabase-database-connection-troubleshooting.md` | L872 | `from src.api.config.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L819 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L1722 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L2255 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L3961 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4146 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4313 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4413 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4582 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4619 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4656 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4693 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L4730 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L5237 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L5523 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/project-structure-compliance-audit.md` | L5937 | `+ from src.api.core.database import db_settings` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/fastapi-and-supabase-connection-troubleshooting.md` | L15569 | `from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1224 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1315 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1404 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1513 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1719 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L1818 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L3150 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L3298 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L3487 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L12350 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L12416 | `+ from src.api.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13314 | `+ from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L13661 | `from src.api.database import get_db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L14386 | `+ from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L18463 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L18679 | `+ from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L19297 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20186 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20304 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20789 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L20836 | `from src.db.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L23914 | `+ from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L25248 | `- from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26640 | `+ from src.api.database import db, DatabaseError` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26811 | `- from src.api.database import engine` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L26815 | `+ from src.api.database import db` |
| `file:///Users/yeondampark/codes/superdisco/video-analytic-agent/.specstory/history/prd-review-and-mvp-development-kickoff.md` | L33840 | `+ from src.api.database import db, DatabaseError` |

</details>

---

_****_





---



---

