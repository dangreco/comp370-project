import json
from pydantic import BaseModel


class Codebook(BaseModel):
    name: str
    description: str
    categories: list["Category"]

    def load(path: str) -> "Codebook":
        with open(path, "r") as f:
            data = json.load(f)
        return Codebook.model_validate(data)

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)

    def to_markdown(self) -> str:
        s = ""
        s += f"# {self.name}\n\n"
        s += f"{self.description}\n\n"
        s += "---\n\n"

        for category in self.categories:
            s += f"## {category.name}\n\n"
            s += f"{category.description}\n\n"
            s += "### Examples\n\n"
            for example in category.examples:
                s += f"- **Input:** {example.input}\n"
                s += f"  - **Include:** {'Yes' if example.include else 'No'}\n"
                s += f"  - **Why:** {example.why}\n\n"
            s += "\n---\n\n"

        return s


class Category(BaseModel):
    name: str
    description: str
    examples: list["Example"]


class Example(BaseModel):
    input: str
    include: bool
    why: str
