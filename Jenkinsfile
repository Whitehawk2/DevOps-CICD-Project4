pipeline {
    agent any
    options {
        buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '5', numToKeepStr: '20')
    }
    environment {
        SECRET = credentials('Mysql-access')
        registry = "whitehawk2/ci-repo-4"
        registryCredential = 'docker_hub'
        dockerImage = ''
    }
    stages {
        stage('SCM checkout and poll') {
            steps {
                script {
                    properties([pipelineTriggers([pollSCM('H/30 * * * *')])])
                }
            }
        }
        stage('prepare python environment') {
            // making sure we have a working python venv with
            // all needed packages thru pip
            steps {
                script{
                    sh 'python3 -m venv pyenv'
                    PYTHON_PATH =  sh(script: 'echo ${WORKSPACE}/pyenv/bin/', returnStdout: true).trim()

                    Py_venv("-m pip install -r ./web_app/requirements.txt")
                }
            }
        }
        stage('run rest_app') {
            steps {
                Python_nohup("./web_app/rest_app.py")
            }
        }
        stage('Backend tests') {
            steps {
                Py_venv("./backend_testing.py")
            }
        }
        stage('Clean env') {
            steps {
                sh 'python3 ./clean_enviornment.py'
            }
        }
        stage('versioning') {
            steps {
                sh "echo IMAGE_TAG=${env.BUILD_NUMBER} > ./web_app/.env"
            }
        }
        stage('build and push image') {
            steps {
                dir("./web_app"){
                    script {
                        dockerImage = docker.build registry + ":$BUILD_NUMBER"
                        docker.withRegistry('', registryCredential) {
                            dockerImage.push()
                        }
                    }
                }
            }
        }
        stage('Docker-compose up') {
            steps {
                dir("./web_app"){
                    sh 'docker-compose up -d'
                }
            }
        }
        stage('Dockerized backend tests') {
            steps {
                Py_venv("./docker-backend_testing.py")
            }
        }
        stage('Clean Docker env'){
            steps {
                dir("./web_app"){
                    sh 'docker-compose down --rmi all'
                }
            }
        }
        stage('Deploy Helm') {
            environment {
                HELM_SQL = credentials('helm_remotemysql')
            }
            steps {
                sh 'helm install alon-proj ./Chart/alon-6.tgz --set image.tag=${BUILD_NUMBER} --set store.dbuser=${HELM_SQL_USR} --set store.dbpas=${HELM_SQL_PSW}'
            }
        }
        stage('get helm service url') {
            steps {
                sh 'minikube service alon-proj-service --url > k8s_url.txt'
            }
        }
        stage('K8S backend tests') {
            steps {
                Py_venv("./k8s_backend_testing.py")
            }
        }
    }
    post {
        always {
            sh 'helm delete alon-proj'
            //sh "docker rmi $registry:$BUILD_NUMBER"
            }
        success {
            echo 'Run finished with 100% success'
        }
    }
}

// Python wrappers
def Py_venv(String command) {
    // an alias to using the python venv
    sh script:". ./pyenv/bin/activate && python3 ${command}", label: "py ${command}"
}
def Python_nohup(String command) {
    // as above, but for live servers with nohup
    sh script:". ./pyenv/bin/activate && nohup python3 ${command} &", label:"python_nohup ${command}"
}
