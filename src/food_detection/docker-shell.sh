set -e
export IMAGE_NAME="food-detection"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run --rm --name $IMAGE_NAME -ti $IMAGE_NAME
# docker-compose up
