# ============================================
# CONFIGURACIÓN DE TERRAFORM
# ============================================
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================
# PROVEEDOR AWS
# ============================================
provider "aws" {
  region = "us-east-1"
}

# ============================================
# VPC - Red Virtual
# ============================================
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "examen-vpc"
  }
}

# ============================================
# SUBNET - Subred pública
# ============================================
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "examen-subnet-public"
  }
}

# ============================================
# INTERNET GATEWAY - Salida a Internet
# ============================================
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "examen-igw"
  }
}

# ============================================
# TABLA DE RUTAS
# ============================================
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "examen-route-table"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ============================================
# SECURITY GROUP - Firewall
# ============================================
resource "aws_security_group" "app" {
  name        = "examen-app-sg"
  description = "Security group para la aplicacion"
  vpc_id      = aws_vpc.main.id

  # Permite SSH (puerto 22)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permite HTTP (puerto 80)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permite la API (puerto 5000)
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permite todo el tráfico saliente
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "examen-sg"
  }
}

# ============================================
# EC2 INSTANCE - Servidor
# ============================================
resource "aws_instance" "app_server" {
  ami           = "ami-0440d3b780d96b29d"  # Amazon Linux 2023
  instance_type = "t2.micro"
  key_name      = "examen-key"
  
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true

  # Script que se ejecuta al iniciar la instancia
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              usermod -a -G docker ec2-user
              
              # Instala docker-compose
              curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              
              echo "Docker instalado correctamente" > /tmp/install-log.txt
              EOF

  tags = {
    Name = "examen-app-server"
  }
}

# ============================================
# OUTPUTS - Información útil
# ============================================
output "instance_public_ip" {
  description = "IP pública de la instancia EC2"
  value       = aws_instance.app_server.public_ip
}

output "instance_id" {
  description = "ID de la instancia EC2"
  value       = aws_instance.app_server.id
}

output "ssh_command" {
  description = "Comando para conectarse por SSH"
  value       = "ssh -i tu-llave.pem ec2-user@${aws_instance.app_server.public_ip}"
}
