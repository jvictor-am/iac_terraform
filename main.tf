provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "note_dell_key" {
  key_name   = "note_dell_key"
  public_key = file("~/.ssh/id_ed25519.pub")
}

resource "aws_security_group" "my_sg" {
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
  }
}

resource "aws_instance" "unifor_ubuntu" {
  ami             = "ami-0866a3c8686eaeeba"
  instance_type   = "t2.micro"
  key_name        = "${aws_key_pair.note_dell_key.key_name}"
  count           = 1
  tags           = {
    Name = "TerraformEC2__Unifor__Ubuntu"
    type = "universidade"
  }
  security_groups = ["${aws_security_group.my_sg.name}"]

  provisioner "file" {
    source      = "web.py"
    destination = "/home/ubuntu/web.py"
  }
  
provisioner "remote-exec" {
  inline = [
    "echo \"export DB_HOST=$(echo ${aws_db_instance.default.endpoint} | cut -d':' -f1)\" >> /home/ubuntu/.bashrc",
    "echo 'export DB_NAME=mydb' >> /home/ubuntu/.bashrc",
    "echo 'export DB_USER=dbadmin' >> /home/ubuntu/.bashrc",
    "echo 'export DB_PASS=password' >> /home/ubuntu/.bashrc",
    "echo 'export DB_PORT=5432' >> /home/ubuntu/.bashrc",
    "source /home/ubuntu/.bashrc",
    "sudo apt update -y",
    "sudo apt install -y python3-pip python3-venv",
    "python3 -m venv /home/ubuntu/venv",
    "/home/ubuntu/venv/bin/pip install streamlit sqlalchemy pandas psycopg2-binary",
    "nohup /home/ubuntu/venv/bin/streamlit run /home/ubuntu/web.py > /home/ubuntu/streamlit.log 2>&1 &"
  ]
}

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_ed25519")
    host        = self.public_ip
  }
}


resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Allow EC2 instances to access RDS"

  ingress {
    from_port   = 5432
    to_port     = 5432
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

resource "aws_db_instance" "default" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "12.20"
  instance_class       = "db.t3.micro"
  db_name              = "mydb"
  username             = "dbadmin"
  password             = "password"
  parameter_group_name = "default.postgres12"
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

output "RDS_ENDPOINT" {
  value = aws_db_instance.default.endpoint
}

output "PUBLIC_IP" {
  value = aws_instance.unifor_ubuntu[0].public_ip
}