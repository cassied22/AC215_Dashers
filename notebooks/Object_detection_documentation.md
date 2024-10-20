## Object Detection Model Selection

We decide to incorporate an object detection model to identify food from the picture uploaded by user. We have experimented object detection models such as MediaPipe['https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector'] and a pretrained food detection model using YOLOV8 as backbone['https://github.com/lannguyen0910/food-recognition'], as well as LLM GPT-4o and gemini-1.5-flash, which can also take images as input. For our initial inspection, we used 10 images containing various food and input into different models and compare the detection results manually.  For MediaPipe and YOLOV8, we directly input the image and check the outputs; for LLMs, we used the image as well as the text "Can you  list the name of food in the picture?" as input. Below we show the results from 3 imgaes. We observed that the LLMs outperm the two object detection model significantly as MediaPipe and YOLOv8 can only identify a very limited set of food. We also observe that LLM has the ability to recognize the food not only from the appearance of food itself, but also utilizes useful information such as packaging (see image 3 below: the image doesn't explicily show eggs but LLM was able to infer it from the carton). Therefore, we eventually decided to utilize LLM for our food detection task.Since both GPT-4o and gemini-1.5-flash, we will make our final decision later after acquiring more labeled food images and constructing a test set to quantitatively evaluate the performance of models.

### Input Image 1
![](food/food1.jpg)

#### Mediapipe Result
![](food/food1_mediapipe.png)

#### YOLOv8 Result
![](food/food1_yolov8.png)

#### GPT Result
![](food/food1_gpt.png)

#### Gemini Result
![](food/food1_gemini.png)

### Input Image 2
![](food/food2.png)

#### Mediapipe Result
![](food/food2_mediapipe.png)

#### YOLOv8 Result
![](food/food2_yolov8.png)

#### GPT Result
![](food/food2_gpt.png)

#### Gemini Result
![](food/food2_gemini.png)

### Input Image 3
![](food/food3.jpg)

#### Mediapipe Result
![](food/food3_mediapipe.png)

#### YOLOv8 Result
![](food/food3_yolov8.png)

#### GPT Result
![](food/food3_gpt.png)

#### Gemini Result
![](food/food3_gemini.png)