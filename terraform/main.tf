
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_ecs_cluster" "manus_cluster" {
  name = "manus-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "manus_backend" {
  family                   = "manus-backend"
  network_mode             = "awsvpc"
  requires_compatibility   = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "simpleyyt/manus-backend:latest"
      
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      
      environment = [
        {
          name  = "API_BASE"
          value = "https://api.openai.com/v1"
        },
        {
          name  = "LOG_LEVEL"
          value = "INFO"
        }
      ]
      
      secrets = [
        {
          name      = "API_KEY"
          valueFrom = aws_ssm_parameter.api_key.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.manus_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "manus_backend" {
  name            = "manus-backend"
  cluster         = aws_ecs_cluster.manus_cluster.id
  task_definition = aws_ecs_task_definition.manus_backend.arn
  desired_count   = 2

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.manus_backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}
