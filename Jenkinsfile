pipeline {
    agent any
    environment {
        AWS_ACCOUNT_ID="476843538485"
        AWS_DEFAULT_REGION="ap-south-1"
        IMAGE_TAG="${BUILD_NUMBER}"
        REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${TASK_DEFINITION_NAME}"
        AWS_VPC="\"awsvpcConfiguration={subnets=[subnet-03063e1a4ef70b9ac],securityGroups=[sg-0e38e57c68c2eb124],assignPublicIp=ENABLED}\""
        FARGATE_CLUSTER_NAME="op-d02-cluster"
        TASK_DEFINITION_NAME="flask-cache-redis_api"
        TASK_DEFINITION_REVISION="4" 
    }


     stages {
        
        stage('Logging into AWS ECR') {
            steps {
                script {
                env.GIT_REPO_NAME = env.GIT_URL.replaceFirst(/^.*\/([^\/]+?).git$/, '$1')
                echo "REPONAME - ${GIT_REPO_NAME}"
                sh "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
                isRepoExist = sh(script:"aws ecr describe-repositories --region ap-south-1 --query 'repositories[].repositoryName'  | grep '${GIT_REPO_NAME}'", returnStatus: true) == 0
                echo "$isRepoExist"
                if (!isRepoExist) {
                        sh "aws ecr create-repository --repository-name ${GIT_REPO_NAME} --image-scanning-configuration scanOnPush=true --region ap-south-1"
                    } else {
                        echo "Repo already Exists, skipping this step ${GIT_REPO_NAME}!"
                    }
                
                }  
            }
        }

        stage('Cloning Git') {
            steps{
                git branch: 'master',
                credentialsId: 'github',
                url: 'https://github.com/baharul/cache-flask.git'
            }
        }

        stage('Build Docker Image'){
            steps {
                script {
                     dockerImage = docker.build "${TASK_DEFINITION_NAME}:${IMAGE_TAG}"
                }
            }
        }

        stage('Push Docker Image'){
            steps {
                script {
                     sh "docker tag ${TASK_DEFINITION_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:$IMAGE_TAG"
                     sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${TASK_DEFINITION_NAME}:${IMAGE_TAG}"
                     sh "docker tag ${TASK_DEFINITION_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:latest"
                     sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${TASK_DEFINITION_NAME}:latest"
                }
            }
        }

        stage('Deploy Fargate Service with New Image') {
            steps {
                script {
                    // BUILD_FULL = sh (script: "git log -1 --pretty=%B | grep '\\[jenkins-full]'", returnStatus: true) == 0
                    env.GIT_REPO_NAME = env.GIT_URL.replaceFirst(/^.*\/([^\/]+?).git$/, '$1')
                    echo "REPONAME - ${GIT_REPO_NAME}"
                    ret = sh(script:'aws ecs list-services --launch-type FARGATE --cluster ${FARGATE_CLUSTER_NAME} --region ap-south-1 --query "serviceArns[]" | grep "${GIT_REPO_NAME}-svc"', returnStatus: true) == 0
                    echo "$ret"
                    if (ret) {
                        echo 'Service Exists!'
                        sh "aws ecs update-service --cluster ${FARGATE_CLUSTER_NAME} --task-definition ${TASK_DEFINITION_NAME}:${TASK_DEFINITION_REVISION} --service ${GIT_REPO_NAME}-svc --desired-count 1 --force-new-deployment"
                    } else {
                        echo 'Service Does not exist! Creating it'
                        status = sh(script:"aws ecs create-service --cluster ${FARGATE_CLUSTER_NAME} --service-name ${GIT_REPO_NAME}-svc --task-definition ${TASK_DEFINITION_NAME} --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:476843538485:targetgroup/python/a36f50beee4c0e05,containerName=flask-cache-redis_api,containerPort=5000 --desired-count 1 --launch-type FARGATE --network-configuration 'awsvpcConfiguration={subnets=[subnet-03063e1a4ef70b9ac],securityGroups=[sg-0e38e57c68c2eb124],assignPublicIp=ENABLED}'", returnStatus: true) == 0
                        echo "redisaml-api-svc - $status"
                    }
                  
                }  
            }
        }
        
     }
}