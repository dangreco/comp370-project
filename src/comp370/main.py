"""
Main entry point for the COMP370 Seinfeld Script Analysis application.

This module sets up and runs a GraphQL API server for querying
Seinfeld episode data including scripts, characters, writers, and metadata.
"""

from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler

from comp370.db import Client as Db
from comp370.gql import schema


def create_app():
    # Initialize database connection
    db = Db()
    db.connect()

    # Create Starlette application
    app = Starlette()

    # Mount GraphQL endpoint with GraphiQL interface
    app.mount(
        "/graphql",
        GraphQLApp(
            schema=schema,
            on_get=make_graphiql_handler(),
            context_value={"session": db.session()},
        ),
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
