"""
Main entry point for the COMP370 Seinfeld Script Analysis application.

This module sets up and runs a GraphQL API server for querying
Seinfeld episode data including scripts, characters, writers, and metadata.
"""

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.responses import FileResponse
from starlette_graphene3 import GraphQLApp

from comp370.db import Client as Db
from comp370.gql import schema
from comp370.constants import DIR_DATA


async def graphiql_redirect(request):
    return RedirectResponse("/gql")


async def dashboard(request):
    return FileResponse(DIR_DATA / "statistics" / "statistics.topics.html")


async def download_db(request):
    return FileResponse(
        DIR_DATA / "comp370.db",
        media_type="application/octet-stream",
        filename="comp370.db",
    )


async def download_stats_tfidf(request):
    return FileResponse(
        DIR_DATA / "statistics" / "statistics.tfidf.csv",
        media_type="application/octet-stream",
        filename="comp370.tf-idf.csv",
    )


async def download_stats_topics(request):
    return FileResponse(
        DIR_DATA / "statistics" / "statistics.topics.csv",
        media_type="application/octet-stream",
        filename="comp370.topics.csv",
    )


async def download_annotations(request):
    return FileResponse(
        DIR_DATA / "annotations" / "annotations.derived.csv",
        media_type="application/octet-stream",
        filename="comp370.annotations.csv",
    )


def create_app():
    # Initialize database connection
    db = Db()
    db.connect()

    graphql_app = GraphQLApp(
        schema=schema,
        context_value={"session": db.session()},
    )

    # Create Starlette application
    app = Starlette(
        routes=[
            Route("/", dashboard),
            Route("/download/db", download_db),
            Route("/download/tf-idf", download_stats_tfidf),
            Route("/download/topics", download_stats_topics),
            Route("/download/annotations", download_annotations),
            Route("/api/graphql", graphql_app),
            Route("/api/graphql/", graphql_app),
            Mount(
                "/gql",
                StaticFiles(
                    directory="public/graphiql",
                    html=True,
                ),
                name="gql",
            ),
            Route("/gql/", graphiql_redirect),
        ]
    )

    return app


def main():
    import uvicorn

    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
