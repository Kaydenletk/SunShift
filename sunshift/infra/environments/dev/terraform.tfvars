aws_region   = "us-east-2"
environment  = "dev"
project_name = "sunshift"

vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-2a", "us-east-2b"]

ecs_cpu           = 256
ecs_memory        = 512
ecs_desired_count = 1
