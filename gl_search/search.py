import concurrent.futures
from asyncio import Future

from .config import settings
from .models import Repo, RepoResult, RequestDescribe, SearchEntryResult, SearchParams, SearchRepoParams
from .utils import retrieve_data


def _retrieve_groups_ids(params: SearchParams) -> list[int]:
    request = RequestDescribe(
        url=f"{settings.GITLAB_URL}/api/v4/groups",
        params={
            "per_page": "100",
            "pagination": "keyset",
            "order_by": "id",
            "sort": "asc",
        },
    )

    data_list: list[int] = retrieve_data(
        request, lambda value: value["id"], max_random_time_for_sleep=params.max_random_time_for_sleep
    )

    return data_list


def _retrieve_repositories_by(group_id: int, params: SearchParams) -> set[Repo]:
    request = RequestDescribe(
        url=f"{settings.GITLAB_URL}/api/v4/groups/{group_id}/projects",
        params={
            "per_page": "100",
            "include_subgroups": "true",
        },
    )
    repos = set(
        retrieve_data(
            request, lambda value: Repo(**value), max_random_time_for_sleep=params.max_random_time_for_sleep
        )
    )

    return {repo for repo in repos if repo.visibility in params.visibility}


def _retrieve_information_from_repositories_of_each_group(
    groups_id: list[int], params: SearchParams
) -> set[Repo]:
    repos: set[Repo] = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=params.max_workers) as executor:
        futures: dict[Future[Repo], int] = {
            executor.submit(_retrieve_repositories_by, group_id, params): group_id for group_id in groups_id
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
    data_list: list[SearchEntryResult] = retrieve_data(
        request,
        lambda value: SearchEntryResult(**value),
        max_random_time_for_sleep=search_params.max_random_time_for_sleep,
    )

    return data_list


def _search_code(
    repos: list[Repo],
    params: SearchParams,
) -> list[RepoResult]:
    results: list[RepoResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=params.max_workers) as executor:
        futures: dict[Future[list[SearchEntryResult]], Repo] = {
            executor.submit(
                _search_in_repo,
                SearchRepoParams(
                    repo_id=repo.id,
                    **params.dict(),
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
        groups_ids = _retrieve_groups_ids(params)

    repos = _retrieve_information_from_repositories_of_each_group(groups_ids, params)
    return _search_code(repos, params)
