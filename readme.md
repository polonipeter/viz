### Deployed version
I recommend to just use the deployed app. The app is deployed on . If you want it is possible to also run the app localy as I included .toml file with compatible versions of poackages. But you have to modify the port and host in the viz.py file as these are set to certain values as this is the code that is running on Render. After setting the preffered port and host just run:
* poetry install 
* poetry shell
* python viz.py
