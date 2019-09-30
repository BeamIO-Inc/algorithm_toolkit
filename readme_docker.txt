Running app as a docker container:

Starting from this folder, navigate to /atkBaseImage

Build the atk base image: docker build . -t atk_base:master

where "atk_base" is the name of the image, and "master" is the tag
That should build a base image for the ATK with all the dependencies installed.
After this, we build a clean project in the docker folder and populate it with the example project in this folder.

Navigate to myproject folder, where the dockerfile for the example project lives

Build the deploy image:
docker build . -t atk_twitter_deploy:master, where again, "atk_twitter_deploy" is the name of the image, and "master" is the tag

Once the image is built, it can be run as a container with the following command:

docker run -p 5000:5000 atk_twitter_deploy:master

The -p 5000:5000 will expose port 5000 to the host machine.

Now go to a web browser on the host machine and type localhost:5000, you should see the atk running locally.

Although the atk is running, we still need to configure the information to call the twitter api.
According to https://developer.twitter.com/en/docs/tweets/search/quick-start/premium-30-day
we need to know: the twitter dev environment label, the consumer api key, and the consumer api secret.

While the atk_twitter_deploy:master container is running, open a new bash shell and run:
docker ps
and observe the container id of the atk container. Now run
docker exec -it [ID] /bin/bash, replacing ID with the container ID. This will open an interactive bash shell within the container,
which will allow us to update the necessary components.
Within this bash shell, navigate to the /atk_project folder and run

echo "TWITTER_ENV_LABEL=\"[...]\"" >> .env
echo "TWITTER_CONSUMER_API_KEY=\"[...]\"" >> .env
echo "TWITTER_CONSUMER_API_SECRET\"[...]\"" >> .env

replacing [...] with your twitter developer environment label, app consumer api key, and app consumer api secret respectively.

You should now be able to set up an algorithm chain using the object detection functionality. The project comes with several example chains.

Running video detection chain:
Run the chain docker_demo, the only step you will need to set up is the first method. In Set Inference Parameters, enter all inference 
parameters. Enter true for twitter graph and object detection graph to view graphs at the end. You will also need to provide the path to 
the video file.



