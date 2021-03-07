# DevOps Experts - CI/CD project
---
**4th part**

Python files reused and adapted from former projects.

## Aim

use Jenkins and Docker + Docker-Compose
to build, test and upload REST API app to docker hub.

Afterwards, it will be deployed and tested using a manully written Helm chart,
K8S and minikube.

`SQL` branch will contain - *eventually* - the version 
utilizing an MySQL pod and persistentVolume in the stack,
while `master` branch has all pipeline and challanges **excluding sql part**
implemented.

### General pipeline:
    1. pull code, run `rest_app.py`
    2. Test the server, clean enviornment afterwards.
    3. build a docker image, and push it to the hub.
    4. Using the build number in jenkins, set an image build number and
       `docker-compose up -d` it.
    5. After giving it a moment to build and stablize, run another test on the
       dockerized app
    6. afterwards, `docker-compose down` and remove the (local) image.
    7. deploy the image from docker hub using a Helm chart.
    8. get the exposed service url via `minikube service <name> -url > k8s-url.txt`
    9. run tests on the k8s deployed app.
    10. clean the env by invoking `helm delete <chart>`

    * Challenges:
	- use secret object for db user and password (instead of hardcode);
	- use configmap to hold db hostname;
	- use "k8s stateful application", "persistentVolume" and "PersistentVolumeClaim" to deploy mysql and use that instead of the online one.

all challenge objectives will be on `Master` branch
	- **Excluding MySQL Challenge!** > will be on `SQL` branch

by Whitehawk, 2021 D:

```python
print('all your base are belong to us')
```
