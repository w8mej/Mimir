
output "instance_public_ip" {
  description = "Public IP of the created instance"
  value       = oci_core_instance.confvm.public_ip
}
