# jakebowers.org

## Local Development

To generate the site locally, you'll need Python 3.14+ and the dependencies listed in `pyproject.toml` (jinja2, pyyaml).

The easiest way to run locally is with [uv](https://docs.astral.sh/uv/):

```bash
uv run python generate_site.py
```

This will automatically install dependencies and run the script.

Note: The production site is built via GitHub Actions, which uses a different setup.
