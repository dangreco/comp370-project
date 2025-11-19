from starlette.testclient import TestClient

from comp370.main import create_app


def main():
    app = create_app()
    client = TestClient(app)

    query = """
    query {
    	fst: episode(season: 1, number: 1) {
    		title
    		writers(first: 10) {
    			edges {
    				node {
    					firstName
    					lastName
    				}
    			}
    		}
    	}
    	lst: episode(season: 9, number: 22) {
    		title
    		writers(first: 10) {
    			edges {
    				node {
    					firstName
    					lastName
    				}
    			}
    		}
    	}
    }
    """

    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()

    # Check the first episode
    assert data["data"]["fst"]["title"] == "Good News, Bad News"
    assert data["data"]["fst"]["writers"]["edges"][0]["node"]["firstName"] == "Jerry"
    assert data["data"]["fst"]["writers"]["edges"][0]["node"]["lastName"] == "Seinfeld"
    assert data["data"]["fst"]["writers"]["edges"][1]["node"]["firstName"] == "Larry"
    assert data["data"]["fst"]["writers"]["edges"][1]["node"]["lastName"] == "David"

    # Check the last episode
    assert data["data"]["lst"]["title"] == "The Finale Part 2"
    assert data["data"]["lst"]["writers"]["edges"][0]["node"]["firstName"] == "Larry"
    assert data["data"]["lst"]["writers"]["edges"][0]["node"]["lastName"] == "David"


if __name__ == "__main__":
    main()
