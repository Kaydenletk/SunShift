terraform {
  backend "s3" {
    bucket         = "sunshift-terraform-state-ACCOUNT_ID"
    key            = "dev/terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
    dynamodb_table = "sunshift-terraform-locks"
  }
}
