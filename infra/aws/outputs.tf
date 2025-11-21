
output "ssh" {
  description = "SSH command to connect to the parent instance"
  value       = "ssh ec2-user@${aws_instance.parent.public_ip}"
}
