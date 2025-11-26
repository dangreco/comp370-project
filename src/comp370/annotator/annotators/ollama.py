import time
import ollama
import requests
from typing import Optional
from pydantic import BaseModel

from comp370.db.models import Line
from ..codebook import Codebook
from ..annotator import Annotator


class OllamaAnnotationResponse(BaseModel):
    category: str


class OllamaAnnotator(Annotator[ollama.Client]):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-oss:120b",
        host: str = "https://ollama.com",
        codebook: Optional[Codebook] = None,
    ) -> None:
        super().__init__(
            ollama.Client(
                host=host,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            ),
            codebook,
        )
        self.model = model
        self.host = host

    def annotate(self, line: Line, max_attempts: int = 5) -> str:
        if not self.codebook:
            raise ValueError("Codebook is required for annotation.")

        exceptions = []
        context = self.context(line, n=5)
        prompt = f"""
        You are an expert in annotating data.
        You were given the following typology in JSON format:

        {self.codebook.model_dump_json(indent=2)}

        Your task is to annotate the proper category for the given data.
        Choose the most appropriate category from the typology.
        Output in JSON according to the specified schema.

        == CONTEXT (previous {len(context)} lines):
        {"\n".join(map(lambda x: f"- {x.character.name}: `{x.dialogue}`", context))}
        == LINE TO ANNOTATE:
        - {line.character.name}: `{line.dialogue}`
        """

        for attempt in range(max_attempts):
            try:
                response = self.engine.chat(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    format=OllamaAnnotationResponse.model_json_schema(),
                )

                if not response or not response.message or not response.message.content:
                    continue

                annotation = OllamaAnnotationResponse.model_validate_json(
                    response.message.content
                )

                for category in self.codebook.categories:
                    if category.name == annotation.category:
                        return annotation.category

                raise ValueError("Category not found in codebook.")
            except Exception as e:
                exceptions.append(e)
                time.sleep(attempt * 2)
                continue

        raise RuntimeError(f"Failed to annotate: {exceptions}")

    def models(self) -> list[str]:
        url = f"{self.host}/api/tags"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return list(set(model["name"] for model in data["models"]))
