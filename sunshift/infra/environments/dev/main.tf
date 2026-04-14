# Networking
module "networking" {
  source = "../../modules/networking"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  enable_nat_gateway = true
  single_nat_gateway = true  # Cost saving for dev
}

# Storage (needs KMS key from security)
module "storage" {
  source = "../../modules/storage"

  project_name = var.project_name
  environment  = var.environment
  kms_key_arn  = module.security.kms_customer_data_key_arn

  depends_on = [module.security]
}

# Database
module "database" {
  source = "../../modules/database"

  project_name = var.project_name
  environment  = var.environment
}

# Security (needs VPC for security groups)
module "security" {
  source = "../../modules/security"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  vpc_cidr_block     = module.networking.vpc_cidr_block
  s3_bucket_arns     = []  # Will be populated after apply
  dynamodb_table_arn = ""  # Will be populated after apply

  depends_on = [module.networking]
}

# ECS
module "ecs" {
  source = "../../modules/ecs"

  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.networking.vpc_id
  public_subnet_ids       = module.networking.public_subnet_ids
  private_subnet_ids      = module.networking.private_subnet_ids
  alb_security_group_id   = module.security.alb_security_group_id
  ecs_security_group_id   = module.security.ecs_tasks_security_group_id
  task_execution_role_arn = module.security.ecs_task_execution_role_arn
  task_role_arn           = module.security.ecs_task_role_arn
  cpu                     = var.ecs_cpu
  memory                  = var.ecs_memory
  desired_count           = var.ecs_desired_count

  environment_variables = {
    SUNSHIFT_DEBUG                   = "true"
    SUNSHIFT_AWS_REGION              = var.aws_region
    SUNSHIFT_S3_BUCKET_CUSTOMER_DATA = module.storage.customer_data_bucket_name
    SUNSHIFT_S3_BUCKET_ML_ARTIFACTS  = module.storage.ml_artifacts_bucket_name
    SUNSHIFT_DYNAMODB_TABLE          = module.database.table_name
  }

  depends_on = [module.security, module.storage, module.database]
}

# Events
module "events" {
  source = "../../modules/events"

  project_name         = var.project_name
  environment          = var.environment
  enable_noaa_polling  = true
  lambda_hurricane_arn = ""  # Will be set when Lambda module is created
}

# Monitoring
module "monitoring" {
  source = "../../modules/monitoring"

  project_name        = var.project_name
  environment         = var.environment
  ecs_cluster_name    = module.ecs.cluster_name
  ecs_service_name    = module.ecs.service_name
  dynamodb_table_name = module.database.table_name
  enable_alarms       = false  # Disable alarms for dev

  depends_on = [module.ecs, module.database]
}
