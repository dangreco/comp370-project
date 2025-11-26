import inquirer
from typing import Optional

from comp370.db.models import Line
from ..codebook import Codebook
from ..annotator import Annotator


class HumanAnnotator(Annotator[None]):
    def __init__(
        self,
        codebook: Optional[Codebook] = None,
    ) -> None:
        super().__init__(None, codebook)

    def annotate(self, line: Line, max_attempts: int = 1) -> str:
        if not self.codebook:
            raise ValueError("Codebook is required for annotation.")

        context = self.context(line, n=3)
        categories = [category.name for category in self.codebook.categories]

        print()
        print()
        print(f"== CONTEXT (previous {len(context)} lines):")
        for ctx_line in context:
            print(f"- {ctx_line.character.name}: `{ctx_line.dialogue}`")
        print("== LINE TO ANNOTATE:")
        print(f"- {line.character.name}: `{line.dialogue}`")
        category = inquirer.list_input(
            "Which category does the above line belong to?",
            choices=categories,
        )
        return category

    def models(self) -> list[str]:
        return []
