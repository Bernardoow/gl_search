from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class SearchParams(BaseModel):
    groups: Optional[str]
    search_code_input: str
    max_workers: int
    visibility: list[str]
    extension: Optional[str]
    filename: Optional[str]
    path: Optional[str]


class SearchRepoParams(BaseModel):
    repo_id: int
    search: str
    extension: Optional[str] = None
    filename: Optional[str] = None
    path: Optional[str] = None

    @property
    def search_with_params(self) -> str:
        search = self.search
        if self.extension:
            search += f" extension:{self.extension}"

        if self.filename:
            search += f" filename:{self.filename}"

        if self.path:
            search += f" path:{self.path}"

        return search


class RequestDescribe(BaseModel):
    url: HttpUrl
    params: dict[str, str] = dict()


class SearchEntryResult(BaseModel):
    path: str
    filename: str
    project_id: int
    data: str
    start_line: int = Field(alias="startline")
    ref: str


class Repo(BaseModel):
    id: int
    name: str
    visibility: str
    web_url: str

    class Config:
        frozen = True


class RepoResult(BaseModel):
    name: str
    web_url: str
    results: list[SearchEntryResult] = list()
