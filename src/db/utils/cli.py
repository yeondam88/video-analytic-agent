import click
from loguru import logger

from src.db.test_connection import test_connection


@click.group()
def cli():
    """Database management CLI"""
    pass


@cli.command()
def test():
    """Test database connection and functionality"""
    success = test_connection()
    if success:
        logger.info("Database tests completed successfully!")
    else:
        logger.error("Database tests failed!")
        exit(1)


if __name__ == "__main__":
    cli() 