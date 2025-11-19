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
from starlette_graphene3 import GraphQLApp

from comp370.db import Client as Db
from comp370.gql import schema


async def graphiql_redirect(request):
    return RedirectResponse("/graphiql/index.html")


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
            Mount("/graphql", graphql_app),
            Mount(
                "/graphiql",
                StaticFiles(directory="public/graphiql"),
                name="graphiql",
            ),
            Route("/graphiql", graphiql_redirect),
        ]
    )

    return app


def main():
    import uvicorn

    app = create_app()
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
