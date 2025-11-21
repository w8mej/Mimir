variable "region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for the parent instance"
  type        = string
  default     = "m5.xlarge"
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 30
}

variable "kms_key_id" {
  description = "KMS key ID for root volume encryption (optional)"
  type        = string
  default     = null
}
