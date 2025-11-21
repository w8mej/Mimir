variable "tenancy_ocid" {
  description = "OCID of the tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of the user"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint of the API key"
  type        = string
}

variable "private_key_path" {
  description = "Path to the API private key"
  type        = string
}

variable "compartment_ocid" {
  description = "OCID of the compartment"
  type        = string
}

variable "region" {
  description = "OCI region"
  type        = string
}

variable "shape" {
  description = "Instance shape"
  type        = string
  default     = "VM.Standard3.Flex"
}

variable "ocpus" {
  description = "Number of OCPUs"
  type        = number
  default     = 4
}

variable "memory_gbs" {
  description = "Memory in GBs"
  type        = number
  default     = 16
}

variable "image_ocid" {
  description = "OCID of the image to use"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for instance access"
  type        = string
}
