from setuptools import setup, find_packages

setup(
    name="video-analytic-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "deepgram-sdk",
        "supabase",
        "asyncio",
        "pytest",
        "pytest-asyncio",
    ],
) 