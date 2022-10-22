# gl-search

This is a lib that use gitlab api to search code.
This code is based in the lib [gitlab-search](https://github.com/phillipj/gitlab-search).

## About

It is a lib to search code at gitlab.
This search can be parameterized with params groups, extension, filename, path, max-workers and visibility.

## How install?

```bash
pip install gl_search
```

## How it works?

The lib use gitlab token (GITLAB_PRIVATE_TOKEN) to search.

## How to setup the token?

Get your token at gitlab and then execute following command to save at home user at the .gl-settings.toml file.

```bash
gl-search setup-token <token>
```

## Can I change gitlab official to self hosted?

Yes you can. Use following command to setup the gitlab-address

```bash
gl-search setup-gitlab-address <self-hosted-gitlab-address>
```

## Where I get gitlab token?

You can get on following link [gitlab-token](https://gitlab.com/-/profile/personal_access_tokens)
The TOKEN must be generated with scope read_api.

## Why this lib was built?

I had problem with repo visibility using a mentioned lib above so I built this script to resolve my problem.

## How to use

```bash
gl-search search test
```

This options is show up below.

```bash
➜  gl_search git:(main) ✗ gl-search search --help
Usage: gl-search search [OPTIONS] SEARCH_CODE_INPUT

  Search command.

Options:
  -p, --path TEXT                 search by Path
  -fn, --filename TEXT            search by filename
  -ext, --extension TEXT          code filename extension :: py,js,cs
  -g, --groups TEXT               search by gitlab group
  -mw, --max-workers INTEGER      number of parallel requests
  -v, --visibility [internal|public|private]
                                  repositories visibility
  -xdr, --max-delay-request INTEGER
  -d, --debug                     Debug :: show urls called.
  --help                          Show this message and exit.
```

## How was made the lib?

The lib was built using click, rich, request, ThreadPoolExecutor.
