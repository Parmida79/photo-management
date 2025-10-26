from os.path import abspath, dirname

import typer
import uvicorn
from dotenv import load_dotenv

from app.config import settings
from app.db import create_db_and_tables, engine, drop_and_create_db
from app.main import app

# Import all models to ensure they're registered with Base.metadata
from app.models import Photo, ColorAnalysis, EmotionAnalysis, DailySummary, Album

load_dotenv()

from sqlmodel import Session, select

cli = typer.Typer(name="Photo Management API")

FILE_DIR = abspath(dirname(__file__))


@cli.command()
def run(
    port: int = settings.port,
    host: str = settings.host,
    log_level: str = settings.log_level,
    reload: bool = settings.reload,
):  # pragma: no cover
    """Run the API server."""
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )


@cli.command()
def create_schema():  # pragma: no cover
    """Implement the schema of project"""
    print(FILE_DIR)
    create_db_and_tables(engine)
    typer.echo('Schema of database has been created')


@cli.command()
def shell():
    """Opens an interactive shell with objects auto imported"""
    _vars = {
        "app": app,
        "settings": settings,
        "engine": engine,
        "cli": cli,
        # "celery": celery,
        "select": select,
        "session": Session(engine),
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(argv=[], user_ns=_vars)
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@cli.command()
def create_database():
    """Drop and Create Database"""
    drop_and_create_db(engine)

if __name__ == "__main__":
    cli()

