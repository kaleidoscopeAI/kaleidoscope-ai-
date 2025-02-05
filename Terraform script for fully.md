# Terraform script for fully deploying the Kaleidoscope AI system on AWS

provider "aws" {
  region = "us-east-1"
}

# S3 Buckets for Data Storage
resource "aws_s3_bucket" "kaleidoscope_raw_data" {
  bucket = "kaleidoscope-raw-data"
  acl    = "private"
}

resource "aws_s3_bucket" "kaleidoscope_processed_data" {
  bucket = "kaleidoscope-processed-data"
  acl    = "private"
}

resource "aws_s3_bucket" "external_data_sources" {
  bucket = "kaleidoscope-external-data"
  acl    = "private"
}

# VPC for Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "kaleidoscope-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.3.0/24", "10.0.4.0/24"]

  enable_nat_gateway = true
}

# ECS Cluster for Containerized Workflows
resource "aws_ecs_cluster" "kaleidoscope" {
  name = "kaleidoscope-cluster"
}

# IAM Role for ECS Tasks
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# ECS Task Definition for Data Processing
resource "aws_ecs_task_definition" "kaleidoscope_task" {
  family                   = "kaleidoscope-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = "1024"
  cpu                      = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      "name": "data-processor",
      "image": "<ECR_IMAGE_URL>",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "environment": [
        { "name": "RAW_DATA_BUCKET", "value": aws_s3_bucket.kaleidoscope_raw_data.bucket },
        { "name": "PROCESSED_DATA_BUCKET", "value": aws_s3_bucket.kaleidoscope_processed_data.bucket }
      ]
    }
  ])
}

# ECS Service to Run Tasks
resource "aws_ecs_service" "kaleidoscope_service" {
  name            = "kaleidoscope-service"
  cluster         = aws_ecs_cluster.kaleidoscope.id
  task_definition = aws_ecs_task_definition.kaleidoscope_task.arn

  desired_count          = 1
  launch_type            = "FARGATE"
  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_service.id]
    assign_public_ip = false
  }
}

# EventBridge Rule to Trigger Tasks on S3 Upload
resource "aws_cloudwatch_event_rule" "s3_upload_trigger" {
  name        = "s3-upload-trigger"
  description = "Triggers ECS task on new data upload to S3"
  event_pattern = <<EOF
{
  "source": ["aws.s3"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["s3.amazonaws.com"],
    "eventName": ["PutObject"],
    "requestParameters": {
      "bucketName": ["${aws_s3_bucket.kaleidoscope_raw_data.bucket}"]
    }
  }
}
EOF
}

resource "aws_cloudwatch_event_target" "ecs_task_target" {
  rule      = aws_cloudwatch_event_rule.s3_upload_trigger.name
  target_id = "ecs-task"

  arn = aws_ecs_cluster.kaleidoscope.arn
  input = jsonencode({
    "cluster": aws_ecs_cluster.kaleidoscope.id,
    "taskDefinition": aws_ecs_task_definition.kaleidoscope_task.arn,
    "launchType": "FARGATE",
    "networkConfiguration": {
      "awsvpcConfiguration": {
        "subnets": module.vpc.private_subnets,
        "securityGroups": [aws_security_group.ecs_service.id],
        "assignPublicIp": "DISABLED"
      }
    }
  })
}

# API Gateway for External Data Sources
resource "aws_apigatewayv2_api" "external_api" {
  name          = "kaleidoscope-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.external_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_function" "external_api_handler" {
  function_name = "kaleidoscopeExternalAPIHandler"
  role          = aws_iam_role.ecs_task_execution.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"

  code {
    s3_bucket = aws_s3_bucket.external_data_sources.bucket
    s3_key    = "lambda_code.zip"
  }
}

resource "aws_apigatewayv2_integration" "external_integration" {
  api_id           = aws_apigatewayv2_api.external_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.external_api_handler.arn
}

resource "aws_apigatewayv2_route" "external_route" {
  api_id    = aws_apigatewayv2_api.external_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.external_integration.id}"
}

