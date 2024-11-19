## Testing & CI
### Continuous Integration Setup
Our project utilizes a CI pipeline that runs on every push or merge to the main branch. The pipeline is implemented using GitHub Actions and includes the following key components:

**Code Build and Linting**
The CI pipeline incorporates an automated build process and code quality checks using linting tools. The specific tools used are:
- Flake8: A Python linting tool that checks for code style and potential errors.
The linting process ensures that the codebase adheres to consistent coding standards and identifies any potential issues or violations.

**Automated Testing**
- Unit Tests: 
  - test_cli_rag.py: Tests individual functions in the cli_rag.py module, including generate_query_embedding, generate_text_embeddings, embed, load, and query. It uses mocking to isolate dependencies and ensure the functions behave as expected.
  - test_gemini_object_detection.py: Tests the identify_food_gemini function and the main function in the gemini_object_detection.py module. It checks the behavior of the functions under different scenarios, such as success and failure cases.
  - test_gpt_object_detection.py: Tests the encode_image, identify_food_gpt, and main functions in the gpt_object_detection.py module. It verifies the correct encoding of images, the functionality of the GPT object detection, and the handling of command-line arguments.
- Integration Tests: 
  - The integration tests are defined in the docker-compose.yml file in the tests/integration directory.
  - The recipe-rag-cli service runs integration tests for the data pipeline component using the command ```python -m pytest tests/integration -v --cov=./ --cov-report=html:coverage/integration/ --cov-report=term```.
  - The food-detection service runs integration tests for the food detection component using the command ```python -m pytest tests/integration -v --cov=./ --cov-report=html:coverage/integration/ --cov-report=term```.
  - These tests verify the interaction and integration between different components of the application.
- System Tests:
The test results are reported within the CI pipeline, providing visibility into the success or failure of each test run.

**Automated Testing Implementation**
The specific testing frameworks and tools used are:

- pytest: A powerful and flexible testing framework for Python.

The tests are organized into separate directories based on their type:

- tests/datapipeline: Contains unit tests for the data pipeline component.
- tests/food-detection: Contains unit tests for the food detection component.
- tests/integration: Contains integration tests that verify the interaction between different components.
- tests/system: Contains system tests that cover user flows and interactions.
  
**Test Coverage Reports**
Our project aims to maintain a minimum code coverage of 50%. The coverage reports are generated using the pytest-cov plugin and are included in the CI pipeline output.

### Run Tests Manually
1. Ensure that you have Python installed on your system.
2. Clone the project repository
3. Navigate to the project directory
4. Install the required dependencies:
   ```pip install -r requirements.txt```
5. Run the tests using pytest:
   ```pytest tests/```
   This will run all the tests located in the tests/ directory and its subdirectories.
6. To generate a coverage report, type the following command:
   ```pytest --cov=src/ --cov-report=html tests/```
    This will run the tests and generate an HTML coverage report in the htmlcov/ directory. You can view the generated html coverage report in htmlcov/index.html in a web browser.