from label_studio_sdk import LabelStudio
from label_studio_sdk.types import RoleBasedTask
from collections.abc import Iterator


class Client:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        project: int = 1,
    ) -> None:
        self.project = project
        self.client = LabelStudio(base_url=base_url, api_key=api_key)

    def get_num_tasks(self) -> int:
        project = self.client.projects.get(id=self.project)
        total = project.task_number
        return total

    def get_tasks(self, page_size: int = 250) -> Iterator[RoleBasedTask]:
        tasks = self.client.tasks.list(
            project=self.project,
            page=1,
            page_size=page_size,
            only_annotated=True,
        )

        for task in tasks:
            yield task
