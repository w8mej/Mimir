terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = var.region
}

data "aws_availability_zones" "available" {}

# Existing VPC
resource "aws_vpc" "mpc" {
  cidr_block = "10.90.0.0/16"
}

# CloudWatch log group for VPC Flow Logs
resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/aws/vpc/flow-logs/mpc"
  retention_in_days = 30
}

# IAM role for VPC Flow Logs to publish to CloudWatch
resource "aws_iam_role" "vpc_flow_logs_role" {
  name = "vpc-flow-logs-to-cwl"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "vpc-flow-logs.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "vpc_flow_logs_policy" {
  name = "vpc-flow-logs-to-cwl-policy"
  role = aws_iam_role.vpc_flow_logs_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      Resource = "*"
    }]
  })
}

# Flow log to CloudWatch
resource "aws_flow_log" "mpc_cwl" {
  vpc_id               = aws_vpc.mpc.id
  traffic_type         = "ALL"
  log_destination_type = "cloud-watch-logs"
  log_group_name       = aws_cloudwatch_log_group.vpc_flow.name
  iam_role_arn         = aws_iam_role.vpc_flow_logs_role.arn
}

resource "aws_subnet" "mpc" {
  vpc_id            = aws_vpc.mpc.id
  cidr_block        = "10.90.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]
}

resource "aws_security_group" "mpc" {
  vpc_id = aws_vpc.mpc.id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "al2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_iam_role" "ec2" {
  name = "mpc-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "mpc-ec2-profile"
  role = aws_iam_role.ec2.name
}

resource "aws_instance" "parent" {
  ami                    = data.aws_ami.al2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.mpc.id
  vpc_security_group_ids = [aws_security_group.mpc.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  enclave_options {
    enabled = true
  }

  # --- Enforce IMDSv2 ---
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required" # IMDSv2 only
    http_put_response_hop_limit = 2          # optional; tighten as needed
    instance_metadata_tags      = "disabled" # or "enabled" if you rely on it
  }

  # --- At-rest encryption (root volume) ---
  root_block_device {
    volume_type = "gp3"
    volume_size = var.root_volume_size
    encrypted   = true
    kms_key_id  = var.kms_key_id # optional; omit to use account default KMS key
  }

  user_data = file("${path.module}/user_data.sh")
}

output "parent_public_ip" {
  value = aws_instance.parent.public_ip
}
