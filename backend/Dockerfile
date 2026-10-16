FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/
# The virtualenv lives outside /backend, so mounting the source does not hide it.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:$PATH
WORKDIR /backend
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen
