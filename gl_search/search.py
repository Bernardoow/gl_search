import concurrent.futures
from asyncio import Future
from typing import Optional

from .config import settings
from .models import Repo, RepoResult, RequestDescribe, SearchEntryResult, SearchParams, SearchRepoParams
from .utils import retrieve_data


def _retrieve_groups_ids() -> list[int]:
    request = RequestDescribe(
        url=f"{settings.GITLAB_URL}/api/v4/groups",
        params={
            "per_page": "100",
            "pagination": "keyset",
            "order_by": "id",
            "sort": "asc",
        },
    )

    data_list: list[int] = retrieve_data(request, lambda value: value["id"])

    return data_list


def _retrieve_repositories_by(group_id: int, visibility_choose: list[str]) -> set[Repo]:
    request = RequestDescribe(
        url=f"{settings.GITLAB_URL}/api/v4/groups/{group_id}/projects",
        params={
            "per_page": "100",
            "include_subgroups": "true",
        },
    )
    repos = set(
        retrieve_data(
            request,
            lambda value: Repo(**value),
        )
    )

    return {repo for repo in repos if repo.visibility in visibility_choose}


def _retrieve_information_from_repositories_of_each_group(
    groups_id: list[int], max_workers: int, visibility_choose: list[str]
) -> set[Repo]:
    repos: set[Repo] = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: dict[Future[Repo], int] = {
            executor.submit(
                _retrieve_repositories_by,
                group_id,
                visibility_choose=visibility_choose,
            ): group_id
            for group_id in groups_id
        }
        for future in concurrent.futures.as_completed(futures):
            data: set[Repo] = future.result()
            repos.update(data)

    return repos


def _search_in_repo(search_params: SearchRepoParams) -> list[SearchEntryResult]:
    params = {"scope": "blobs", "search": search_params.search_with_params}

    request = RequestDescribe(
        url=f"{settings.GITLAB_URL}/api/v4/projects/{search_params.repo_id}/search",
        params=params,
    )
    data_list: list[SearchEntryResult] = retrieve_data(request, lambda value: SearchEntryResult(**value))

    return data_list


def _search_code(
    repos: list[Repo],
    search_code_input: str,
    max_workers: int,
    extension: Optional[str] = None,
    filename: Optional[str] = None,
    path: Optional[str] = None,
) -> list[RepoResult]:
    results: list[RepoResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: dict[Future[list[SearchEntryResult]], Repo] = {
            executor.submit(
                _search_in_repo,
                SearchRepoParams(
                    repo_id=repo.id,
                    search=search_code_input,
                    extension=extension,
                    filename=filename,
                    path=path,
                ),
            ): repo
            for repo in repos
        }
        for future in concurrent.futures.as_completed(futures):
            repo: Repo = futures[future]

            data: list[SearchEntryResult] = future.result()

            results.append(RepoResult(name=repo.name, web_url=repo.web_url, results=data))

    return results


def search(params: SearchParams) -> list[dict[str, str]]:
    if params.groups:
        groups_ids = list(map(int, params.groups.split(",")))
    else:
        groups_ids = _retrieve_groups_ids()

    repos = _retrieve_information_from_repositories_of_each_group(
        groups_ids, params.max_workers, params.visibility
    )
    return _search_code(
        repos, params.search_code_input, params.max_workers, params.extension, params.filename, params.path
    )
