from starlette.testclient import TestClient

from comp370.main import create_app


def main():
    app = create_app()
    client = TestClient(app)

    query = """
    query {
        jerry: character(name: "Jerry Seinfeld") {
            actors(first: 10) {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    	fst: episode(season: 1, number: 1) {
    		title
    		writers(first: 10) {
    			edges {
    				node {
    					name
    				}
    			}
    		}
    	}
    	lst: episode(season: 9, number: 22) {
    		title
    		writers(first: 10) {
    			edges {
    				node {
       					name
    				}
    			}
    		}
    	}
    }
    """

    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()

    # Check Jerry
    assert (
        data["data"]["jerry"]["actors"]["edges"][0]["node"]["name"] == "Jerry Seinfeld"
    )

    # Check the first episode
    assert data["data"]["fst"]["title"] == "Good News, Bad News"
    assert (
        data["data"]["fst"]["writers"]["edges"][0]["node"]["name"] == "Jerry Seinfeld"
    )
    assert data["data"]["fst"]["writers"]["edges"][1]["node"]["name"] == "Larry David"

    # Check the last episode
    assert data["data"]["lst"]["title"] == "The Finale Part 2"
    assert data["data"]["lst"]["writers"]["edges"][0]["node"]["name"] == "Larry David"


if __name__ == "__main__":
    main()
