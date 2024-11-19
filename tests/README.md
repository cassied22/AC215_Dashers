## Testing & CI
### Continuous Integration Setup
Our project utilizes a CI pipeline that runs on every push or merge to the main branch. The pipeline is implemented using GitHub Actions and includes the following key components:
**Code Build and Linting**
The CI pipeline incorporates an automated build process and code quality checks using linting tools. The specific tools used are:
- Flake8: A Python linting tool that checks for code style and potential errors.
The linting process ensures that the codebase adheres to consistent coding standards and identifies any potential issues or violations.

**Automated Testing**
- Unit Tests: 
- Integration Tests: 
- System Tests:
The test results are reported within the CI pipeline, providing visibility into the success or failure of each test run.

**Automated Testing Implementation**
The specific testing frameworks and tools used are:

- ##pytest: A powerful and flexible testing framework for Python.

The tests are organized into separate directories based on their type:

- tests/datapipeline: Contains unit tests for the data pipeline component.
- tests/food-detection: Contains unit tests for the food detection component.
- tests/integration: Contains integration tests that verify the interaction between different components.
- tests/system: Contains system tests that cover user flows and interactions.
  
**Test Coverage Reports**
Test coverage reports are generated as part of the CI pipeline to monitor the extent to which the codebase is covered by tests. The project aims to maintain a minimum code coverage of 50%. The coverage reports are generated using the pytest-cov plugin and are included in the CI pipeline output.

## Run Tests Manually
1. Ensure that you have Python installed on your system.
2. Clone the project repository
3. Navigate to the project directory
4. Install the required dependencies:
   ```pip install -r requirements.txt```
5. Run the tests using pytest:
   ```pytest tests/```
   This will discover and run all the tests located in the tests/ directory and its subdirectories.
6. To generate a coverage report, type the following command:
   ```pytest --cov=src/ --cov-report=html tests/```
    This will run the tests and generate an HTML coverage report in the htmlcov/ directory. You can view the generated html coverage report in htmlcov/index.html in a web browser.