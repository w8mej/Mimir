terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 6.0.0"
    }
  }
  required_version = ">= 1.6.0"
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

resource "oci_core_virtual_network" "mpc" {
  cidr_block     = "10.91.0.0/16"
  compartment_id = var.compartment_ocid
  display_name   = "mpc-vcn"
}

resource "oci_core_subnet" "mpc" {
  cidr_block                 = "10.91.1.0/24"
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_virtual_network.mpc.id
  display_name               = "mpc-subnet"
  prohibit_public_ip_on_vnic = false
}

resource "oci_core_internet_gateway" "mpc" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.mpc.id
  display_name   = "mpc-igw"
}

resource "oci_core_default_route_table" "rt" {
  manage_default_resource_id = oci_core_virtual_network.mpc.default_route_table_id

  route_rules = [
    {
      cidr_block        = "0.0.0.0/0"
      network_entity_id = oci_core_internet_gateway.mpc.id
      destination       = "0.0.0.0/0"
      destination_type  = "CIDR_BLOCK"
    }
  ]
}

resource "oci_core_instance" "confvm" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  shape               = var.shape

  shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_gbs
  }

  source_details {
    source_type = "image"
    image_id    = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.mpc.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/user_data.sh"))
  }

  display_name                        = "mpc-confidential-vm"
  is_pv_encryption_in_transit_enabled = true
  is_live_migration_preferred         = false
}

output "instance_public_ip" {
  value = oci_core_instance.confvm.public_ip
}
