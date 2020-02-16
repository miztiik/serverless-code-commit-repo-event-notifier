# Serverless AWS CodeCommit Repository Event Notifier

A simple lambda function that gets triggerred in response to an AWS CodeCommit repository events and update the team in slack.

![Fig : Serverless AWS CodeCommit Repository Event Notifier](https://raw.githubusercontent.com/miztiik/serverless-code-commit-repo-event-notifier/master/images/serverless-code-commit-repo-event-notifier.png)

#### Follow this article in [Youtube](https://www.youtube.com/watch?v=5UC8adwht4k&list=PLxzKY3wu0_FKuCD3X6Uc_XjCKXA5-zmIW&index=5)

1. ## Pre-Requisities

    We will need the following pre-requisites to successfully complete this activity,
    - `AWS CodeCommit Repo` - [Get help here to setup CodeCommit Repo](https://youtu.be/9vYdORRoQdg)
    - IAM Role - _i.e_ `Lambda Service Role` - _with managed permissions_ [Get Help for setting up IAM Role](https://www.youtube.com/watch?v=5g0Cuq-qKA0&list=PLxzKY3wu0_FLaF9Xzpyd9p4zRCikkD9lE&index=11)
        - `AWSLambdaBasicExecutionRole` - To allow Lambda to log events
        - `AWSCodeCommitReadOnly` - To allow Lambda to read repo metadata

1. ## Configure Lambda Function

    - The python script is written(_and tested_) in `Python 3.7`.
    - `Copy` the code from `serverless-code-commit-repo-event-notifier` in this repo to the lambda function
    - _Optional:_ Add slack `slack_webhook_url` in the environment variable
    - `Save` the lambda function

1. ## Configure Lambda Triggers

    - Choose **AWS CodeCommit** from the list of services.

    ![Fig : Serverless AWS CodeCommit Repository Event Notifier](https://docs.aws.amazon.com/codecommit/latest/userguide/images/codecommit-lambda-trigger.png)

    - In **Repository name**, choose your repository name.

    - In **Trigger name**, enter a name for the trigger.
    - In **Events**, choose the repository events that trigger the Lambda function, for example, choose **All repository events**.
    - In **Branches**, Choose **All branches**, if you want the trigger to apply to all branches of the repository.
    - In **Custom data**, _Optional_: Leave empty for now.
    - Choose **Next**.

    Now your lambda function should be triggered when ever there is a CodeCommit event in your repository

1. Testing the solution

    Create a new commit/branch in your repo, you should be getting the message in Slack(if configured).
