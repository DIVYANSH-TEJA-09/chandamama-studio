# Contributing to Chandamama Studio

Thank you for your interest in contributing to Chandamama Studio! We welcome contributions from everyone.

## Getting Started

1.  **Fork the repository** on GitLab.
2.  **Clone your fork** locally:
    ```bash
    git clone https://gitlab.com/your-username/chandamama-studio.git
    cd chandamama-studio
    ```
3.  **Install dependencies**:
    This project uses `uv` for dependency management.
    ```bash
    uv sync
    ```
    Or using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Python Version

This project requires **Python 3.11** or higher.

## Reporting Issues

-   Search existing issues to avoid duplicates.
-   Use the **Bug** or **Feature** issue templates when creating a new issue.
-   Provide as much detail as possible, including steps to reproduce for bugs.

## Submitting Merge Requests

1.  Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
2.  Make your changes and commit them with clear, descriptive messages.
3.  Push your branch to your fork.
4.  Submit a Merge Request (MR) to the `main` branch.
5.  Use the **Default** MR template and fill in the required details.

## Code Style

-   We use **Ruff** for linting and formatting.
-   Please ensure your code passes linting before submitting:
    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

## License

By contributing, you agree that your contributions will be licensed under the **AGPLv3** License.
