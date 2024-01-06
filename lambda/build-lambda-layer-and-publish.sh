#!/bin/sh

NAME=$1
DESCRIPTION=$2

# See https://repost.aws/knowledge-center/lambda-layer-simulated-docker
echo 'Cleaning up in preparation ...'
rm -f "tmp/${NAME}.zip"
rm -rf tmp/python
mkdir -p tmp/python
echo 'Installing libraries using docker container ...'
docker run -v "$PWD/../":/var/task "public.ecr.aws/sam/build-python3.11" /bin/sh -c "cd example_app_everything; pip install -r requirements.txt -t tmp/python/lib/python3.11/site-packages/; exit"
echo "Copying .py files ..."
cp ../*.py tmp/python/lib/python3.11/site-packages/
cp ../static tmp/python/lib/python3.11/site-packages/
echo "Zipping ..."
cd tmp
zip -r "${NAME}.zip" python
cd ..
echo "Publishing ..."
aws lambda publish-layer-version --layer-name "${NAME}" --description "${DESCRIPTION}" --zip-file "fileb://tmp/${NAME}.zip" --compatible-runtimes "python3.11"
echo "done."
