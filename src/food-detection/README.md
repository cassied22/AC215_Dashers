# Object Detection Module

This module serves the food detection functionality: given a picture, output list of detected food. 

## Instruction for running docker 

- Run docker container by using:
```chmod +x docker-shell.sh```
```sh docker-shell.sh```


## Object Detection Model Selection

We have experimented with object detection models including MediaPipe['https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector'] and a pretrained food detection model using YOLOV8 as backbone['https://github.com/lannguyen0910/food-recognition']. We also experimented with LLMs that also accept images as input including  GPT-4o and gemini-1.5-flash. For our initial inspection, we used 10 images containing various food and input them into different models to compare the detection results manually.  For MediaPipe and YOLOV8, we directly input the images and check the outputs; for LLMs, we used the image as well as the text "Can you  list the name of food in the picture?" as input. Below we show the results from 3 images. We observed that both LLMs outperforms the two object detection models significantly as MediaPipe and YOLOv8 can only identify a very limited set of food. We also observe that LLM has the ability to recognize the food not only from the appearance of food itself, but also utilizes useful information such as packaging (see image 3 below: the image doesn't explicily show eggs but LLM was able to infer it from the carton). Therefore, we eventually decided to utilize LLM for our food detection task. Since both GPT-4o and gemini-1.5-flash work quite well, we incorporated the code for both approaches in this folder. However, for our final frontend application, we decided to use GPT due to its more consistent/accurate performance in corretcly identifying food items from the test images.

### Input Image 1
![](data/exp_results/food1.jpg)

#### Mediapipe Result
![](data/exp_results/food1_mediapipe.png)

#### YOLOv8 Result
![](data/exp_results/food1_yolov8.png)

#### GPT Result
![](data/exp_results/food1_gpt.png)

#### Gemini Result
![](data/exp_results/food1_gemini.png)

### Input Image 2
![](data/exp_results/food2.png)

#### Mediapipe Result
![](data/exp_results/food2_mediapipe.png)

#### YOLOv8 Result
![](data/exp_results/food2_yolov8.png)

#### GPT Result
![](data/exp_results/food2_gpt.png)

#### Gemini Result
![](data/exp_results/food2_gemini.png)

### Input Image 3
![](data/exp_results/food3.jpg)

#### Mediapipe Result
![](data/exp_results/food3_mediapipe.png)

#### YOLOv8 Result
![](data/exp_results/food3_yolov8.png)

#### GPT Result
![](data/exp_results/food3_gpt.png)

#### Gemini Result
![](data/exp_results/food3_gemini.png)