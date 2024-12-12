# AC215 - Milestone5 - Daily Meal Assistant - "What to Eat Today"

**Team Members**

Hanqi(Hanna) Zeng(hanqizeng@hsph.harvard.edu)  <br/> 
Chris Wang(ywang3@hsph.harvard.edu)   <br/> 
Selina Qian(jingyun_qian@hsph.harvard.edu) <br/> 
Shiyu Ma(shiyuma@g.harvard.edu)  <br/> 
Cassie Dai(cdai@g.harvard.edu) <br/> 


**Group Name**
Dashers

**Project**
In this project, we aim to develop an app that serves as a personal meal assistant, helping users track their available ingredients, suggest healthy recipes, and recommend nearby restaurants based on user preferences and current inventory. The app will combine advanced AI tools like object detection and large language models (LLMs) to provide tailored meal recommendations and route suggestions for dining out. <br/>

----
### Milestone5 ###

In this final milestone, we focus on three key areas:
- Production-ready deployment with Kubernetes and Ansible.
- Project demonstration and documentation.
- Public communication of results through a live showcase.

## Prerequistes and Setup Instructions
### Build Recipe Vector Database
Navigate to src/datapipeline directory:
```bash
cd src/datapipeline
```
Build container:
```bash
sh docker-shell.sh
```
Run cli_rag.py to download recipe vector database and build Chromadb:
```bash
python cli_rag.py --download --load
```
Note: Keep this container running while proceding to the next container.
### Run API Server
Navigate to src/api-service:
```bash
cd src/api-service
```
Build container:
```bash
sh docker-shell.sh
```
Start server:
```bash
uvicorn_server
```
Note: Keep this container running while proceding to the next container.
### Run Frontend 
Navigate to src/frontend_react:
```bash
cd src/frontend_react
```
Build container:
```bash
sh docker-shell.sh
```
Start frontend:
```bash
npm install
npm run dev
```

## Deployment instructions
TODO

## Usage details and examples
We have deployed our application at http://35.188.13.243/ for all users to try out. 

To run the application locally, please refer to the Prerequisites and Setup Instructions above.

Our application offers a smart solution for daily meal planning from a single image. Key features include:

- Ingredients Detection: Automatically identify ingredients in the uploaded image.
- Recipe Generation: Generate personalized recipes based on detected ingredients.
- Interactive AI Chat Agent: Allow user to refine and customize generated recipes through an intuitive chat interface with our AI agent.
- Video Demonstration: Provide users with option to watch step-by-step video instructions for cooking the generated recipes.
- Restaurant Search: Allow users to search for nearby restaurants instead if they are not in the mood to cook.

Our platform is designed to streamline the cooking experience, whether users are looking to create a meal from scratch or dine out conveniently.

### Example Usage:

#### Example 1: The start of the page: click on "Get Started" to go to the image upload page.

<img src="images/usage/1.png">

Upload an image of a refridgerator filled with raw ingredients:
<img src="images/usage/2.png">
<img src="images/usage/3.png">

See the list of detected results here. We have two AI assistants to choose from: the LLM without RAG and LLM with RAG; this time we can try the LLM without RAG, click on the "AI Assistant(LLM)" and proceed:

<img src="images/usage/4.png">

get recipe in the chat box page, check the generated recipe and detail use of ingredients:
<img src="images/usage/5.png">

Click on the 'Watch a Video' button on the buttom left corner of the chat page above, get the searched results for youtube videos and blog posts related to the generated recipe:
<img src="images/usage/5.5.png">

You can always click reload below to get different search results:
<img src="images/usage/6.png">

Click on the first search result link, and watch the video on youtube about how to make your dish: 

<img src="images/usage/7.png">

Example 2: The start of the page: click on "Get Started" to go to the image upload page.

<img src="images/usage2/1.png">

Upload an image of a dish to learn the ingredients and how to cook it:
<img src="images/usage2/3.png">


See the identified ingredients here and click on the AI expert this time to proceed:
<img src="images/usage2/2.png">

Get recipe in the chat box page, check the generated recipe and detail use of ingredients:

<img src="images/usage2/4..png">

Continue chatting with the AI assistant to refine the recipe based on your personal preference:

<img src="images/usage2/5.2.png">


If you do not feel like cooking yourself, click on the Dine Out Button at the bottom of the chat page and you will be able search for restaurants on Google Map as below 
<img src="images/usage2/7.png">



## Known issues and limitations
Here are a few limitations we've identified in the current version of our application:
 1. Geolocation Restrictions: The deployed public website currently cannot directly retrieve the user's real-time location when using the Google Maps function. However, running the application locally enables accurate location retrieval.
 2. RAG LLM Flexibility: We've observed that the RAG-empowered LLM can sometimes be less flexible due to its reliance on a specific database. To address this, we plan to implement customized databases for each user to enhance the accuracy and relevance of RAG-based suggestions in the future.
 3. User Preference Profiling: While we track user preferences to some extent through chat history, we haven't yet implemented a comprehensive system to build a holistic preference profile for each user at the start of a new chat. This can lead to less ideal initial recipe suggestions, requiring more interaction between the user and the AI assistant to refine the recommendations.

## Technical Implementation

### CI and Test

We have a functioning CI pipeline implemented using GitHub Actions that:
- runs unit tests across every container
- runs integration tests across the exposed API
- deploys updates to the Kubernetes cluster
- achieves test coverage over 90% of the lines 
  
on every pull request or merge to the main branch. It includes the following key components:

#### Code Build and Linting
The CI pipeline incorporates an automated build process and code quality checks using linting tools. The specific tools used are:
- Flake8: A Python linting tool that checks for code style and potential errors.
The linting process ensures that the codebase adheres to consistent coding standards and identifies any potential issues or violations.

#### Automated Testing
The specific testing frameworks and tools used are:

- pytest: A powerful and flexible testing framework for Python.

The tests are organized into separate directories based on their type:

- Unit tests: Testing the functionality of each component in isolation
  - tests/datapipeline
  - tests/food-detection
  - tests/ml-pipeline
  - tests/api-service
- Integration(System) test: Testing the interaction between different components
  - tests/integration

#### Unit Tests: 
We write unit tests for all the Python scripts in our repo, including the source code for each component(container) and the scripts to deploy API endpoints. 
##### datapipeline
  - **tests/datapipeline/test_cli_rag.py**: Tests all the functions in **src/datapipeline/cli_rag.py**. It validates the functionality of a CLI-based recipe recommendation system by mocking external dependencies and ensuring correct behavior for core operations like embedding generation, data loading, querying, chatting, downloading, and argument parsing.
##### food-detection
  - **tests/food-detection/test_gemini_object_detection.py**: Tests all the functions in **src/food-detection/gemini_object_detection.py**, including identify_food_gemini and the main function. It tests the Gemini-based object detection system by mocking API configuration, file handling, and command-line inputs to validate correct functionality and error handling.
  - **tests/food-detection/test_gpt_object_detection.py**: Tests all the functions in **src/food-detection/gpt_object_detection.py**, including encode_image, identify_food_gpt, and main functions. It verifies the functionality of a GPT-based object detection system by mocking file handling, external API calls, and command-line inputs to ensure correct behavior for image encoding, API requests, and program execution with various scenarios.
##### ml-pipeline   
  - **tests/ml-pipeline/**: There are 4 test scripts in this folder, corresponding to each Python script in the **src/ml-pipeline**:
    
    - **tests/ml-pipeline/test_cli.py.py**: validates the functionality of **src/ml-pipeline/cli.py** by testing individual components such as UUID generation, data processing, model training, and evaluation through mock objects.
    - **tests/ml-pipeline/test_data_process.py**: tests the functionality of **src/ml-pipeline/data_process.py** by mocking GCP storage interactions, file operations, and data transformations to validate the behavior of clean, prepare, and upload functions.
    - **tests/ml-pipeline/test_model_evaluation.py**: tests **src/ml-pipeline/model_evaluation.py**, including ingredient extraction, match percentage calculation, and valid pair computation. It validates end-to-end evaluation with mocked data, storage, and model dependencies to ensure accurate ingredient-based content generation.
    - **tests/ml-pipeline/test_model_training.py**: validates the gemini_fine_tuning function in **src/ml-pipeline/model_training.py** by mocking Vertex AI's fine-tuning process, including initialization, training, and job completion. It ensures correct parameter passing and verifies expected outputs for the tuned model and endpoint names.
##### api-service 
  - **tests/api-service/**: There are 9 test scripts in this folder, corresponding to each Python script in the **src/api-service/api**:
    
    - **tests/api-service/test_service.py**: tests various API routes in **src/api-service/api/service.py**
    - **tests/api-service/test_youtube.py**, **tests/api-service/test_llm_chat.py**, **tests/api-service/test_llm_detection_chat.py**, **tests/api-service/test_llm_rag_chat.py** tests 4 scripts to deploy API endpoints in **src/api-service/api/routers/** by verifying API's functionality via mocking external dependencies, without making actual API calls
    - **tests/api-service/test_chat_utils.py**, **tests/api-service/test_llm_utils.py**, **tests/api-service/test_llm_detection_utils.py**, **tests/api-service/test_llm_rag_utils.py** tests 4 utils scripts in **src/api-service/api/utils/** by verifying the functionality of API utility functions, including chat session creation, query embedding generation, and response handling. It uses mocking to simulate external dependencies like models, collections, and sessions, ensuring correct behavior and error handling in functions like generate_query_embedding, generate_chat_response, and rebuild_chat_session.

    We achieved code coverage of over 90% on unit test based on the coverage report below.

    <img src="images/coverage_datapipeline.jpg" width="500">
    <img src="images/coverage_food.jpg" width="500">
    <img src="images/coverage_ml.jpg" width="500">
    <img src="images/coverage_api.jpg" width="500">

#### Integration Tests:
  - The integration tests environment is defined in the docker-compose.yml file in the tests/integration directory. In this integrated environment, the container for recipe-rag-cli, chromadb, api-service, and food-detection service will all be run.
  - For the integration test, in **tests/integration/test_api_service.py**, we test the functionality of each API endpoint by checking the response code when calling these APIs using our mock input. Also, in **tests/integration/test_api_service::test_full_workflow**, we verify the interaction and integration between different application components by simulating a complete backend API calling workflow for users uploading images, getting text responses from LLM, chatting with LLM, and getting video search results from Youtube.
  - The test results are reported within the CI pipeline, providing visibility into the success or failure of each test run. 

    <img src="images/coverage_integration.png">
#### System Tests:
  - We also have a system test, in **tests/integration/test_front_end.py**, to verify end-to-end user interaction in web browser. To run it locally, you need to follow the setup instructions from the root page [README.md](../README.md#prerequistes-and-setup-instructions) to start the API server, install Selenium through ```pip install selenium``` and run ```pytest test_front_end.py``` to trigger the testing Chrome browser.
  - The test automates a browser-based workflow to validate the UI and functionality of our app. It covers image upload with preview and table validation, starting a chat to process detected items and verify chatbot responses, and initiating a YouTube search to ensure results are displayed in a table.

    <img src="images/coverage_system.png">


### Machine Learning Workflow

We have developed a production-ready machine learning workflow including the following components: Data Processor, Model Training/Evaluation and Model Evaluation. We have also set up a CI/CD pipeline to trigger automated data processing, model retraining, and pipeline running. For detailed documentation on our machine learning workflow, please refer to [ML Documentation](src/ml-pipeline/README.md)

### Docker Containers

- [API Service](src/api-service): this container includes implementations related to the api services
- [Data Versioning](src/data-versioning): this container serves the data version controls functionality.
- [Datapipeline](src/datapieline): this container contains implementation of RAG: it prepares data for LLM with RAG, including tasks such as chunking, embedding, and populating the vector database, and output recommended recipe.
- [deployment](src/deployment): this container is responsible for deployment of our application. 
- [food-detection](src/food-detection): this container contains implementation for food detection functionality.
- [frontend_react](src/frontend_react): this container contains frontend implementations.
- [ml-pipeline](src/ml-pipeline): this container contains implementations related to machine learning workflow

Instructions for running dockers above locally:
```bash
cd src/...
sh docker-shell.sh
```

### Notebooks/Reports

- [Notebook](notebook) contains our DVC retrieval procedure, EDA for the recipe data, and the model selection insights for food detection models.
- [Reports](reports) contains different versions of our app's flowchart and a comprehensive description pdf of our project. 
- [Midterm](midterm_presentation) contains the slides for our midterm project pitch.
- [Image](images) contains all the figures used in the readme. 


