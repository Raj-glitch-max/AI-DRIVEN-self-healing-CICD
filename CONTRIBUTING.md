# Contributing to AI-Driven Self-Healing CI/CD

Thank you for your interest in contributing to the AI-Driven Self-Healing CI/CD platform! We welcome contributions from the community to help make this project better.

## Development Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- OpenAI API Key

### Local Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Raj-glitch-max/AI-DRIVEN-self-healing-CICD.git
    cd AI-DRIVEN-self-healing-CICD
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    ```bash
    cp .env.example .env
    # Edit .env with your OpenAI API key and GitHub token
    ```

5.  **Run Tests**
    ```bash
    pytest tests/
    ```

## Contributing Workflow

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally.
3.  **Create a branch** for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Make your changes**. Ensure code is clean and documented.
5.  **Run tests** to ensure no regressions:
    ```bash
    pytest
    ```
6.  **Commit your changes** using conventional commits:
    ```bash
    git commit -m "feat(healer): add new error detection pattern"
    ```
7.  **Push to your fork**:
    ```bash
    git push origin feature/your-feature-name
    ```
8.  **Submit a Pull Request** to the `main` branch of the original repository.

## Code Style

-   **Python**: We follow PEP 8. Please use `flake8` or `black` to format your code.
-   **Documentation**: Ensure all functions and classes have docstrings.
-   **Type Hinting**: Use Python type hints for better code clarity.

## Testing Guidelines

-   Add unit tests for any new functionality.
-   Ensure existing tests pass.
-   We aim for high test coverage.

## Pull Request Process

-   Fill out the Pull Request template completely.
-   Link any related issues.
-   Await review from maintainers. We aim to review PRs within a few days.

## Reporting Issues

-   Use the Bug Report template for bugs.
-   Use the Feature Request template for new ideas.
-   Check existing issues before creating a new one.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
