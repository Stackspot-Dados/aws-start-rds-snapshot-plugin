resource "aws_iam_role" "iam_for_lambda" {
  name = "{{inputs.role_name_for_lambda}}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


# Para o deploy funcionar, gerar um arquivo .zip do arquivo main.py com o nome lambda_function.zip
resource "aws_lambda_function" "lambda" {
  filename      = "lambda_function.zip"
  function_name = "{{lambda_name}}"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "main.lambda_handler"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("lambda_function.zip")

  runtime = "python3.8"

  environment {
    variables = {
      DBS_SNAPSHOTS = "test" # inserir nomes dos snapshots aqui
      SUFIXO_SNAPSHOT = "test" # inserir sufixo dos snapshots aqui
      DBS_INSTANCES_SNAPSHOTS = "test" # inserir nome da instância do banco de dados aqui
    }
  }
}