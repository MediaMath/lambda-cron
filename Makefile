cfn_stack   = LambdaCron-${env}
template    = template.cfn.yml
code_bucket = lambda-cron.${env}.mmknox
cur-dir     = $(shell pwd)
timestamp   = $(shell date +%s)
code_file   = code_$(timestamp).zip
datetime_formatted = $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

init:
	rm -f code.zip
	pip install --requirement requirements.txt --target=/tmp/knox_lambda_cron_dependencies --ignore-installed
	cd /tmp/knox_lambda_cron_dependencies; zip -r $(cur-dir)/code.zip .
	rm -rf /tmp/knox_lambda_cron_dependencies
	zip code.zip main.py
	zip -r code.zip src
	aws s3api create-bucket --bucket $(code_bucket) --region us-east-1
	aws s3 cp code.zip s3://$(code_bucket)/code/${code_file}
	aws cloudformation create-stack --stack-name $(cfn_stack) \
				--template-body file://$(template) \
				--parameters ParameterKey=CodeS3Key,ParameterValue=code/$(code_file) \
					ParameterKey=Environment,ParameterValue=${env} \
					ParameterKey=State,ParameterValue=${state} \
				--capabilities CAPABILITY_NAMED_IAM \
				--region us-east-1
	aws cloudformation wait stack-create-complete --stack-name $(cfn_stack) --region us-east-1

deploy:
	rm -f code.zip
	pip install --requirement requirements.txt --target=/tmp/knox_lambda_cron_dependencies --ignore-installed
	cd /tmp/knox_lambda_cron_dependencies; zip -r $(cur-dir)/code.zip .
	rm -rf /tmp/knox_lambda_cron_dependencies
	zip code.zip main.py
	zip -r code.zip src
	aws s3 cp code.zip s3://$(code_bucket)/code/${code_file}
	aws cloudformation update-stack --stack-name $(cfn_stack) \
				--template-body file://$(template) \
				--parameters ParameterKey=CodeS3Key,ParameterValue=code/$(code_file) \
					ParameterKey=Environment,ParameterValue=${env} \
					ParameterKey=State,ParameterValue=${state} \
				--capabilities CAPABILITY_NAMED_IAM \
				--region us-east-1
	aws cloudformation wait stack-update-complete --stack-name $(cfn_stack) --region us-east-1

update-stack:
	aws cloudformation update-stack --stack-name $(cfn_stack) \
				--template-body file://$(template) \
				--parameters ParameterKey=CodeS3Key,UsePreviousValue=true \
					ParameterKey=Environment,ParameterValue=${env} \
					ParameterKey=State,ParameterValue=${state} \
				--capabilities CAPABILITY_NAMED_IAM \
				--region us-east-1
	aws cloudformation wait stack-update-complete --stack-name $(cfn_stack) --region us-east-1

invoke:
	echo '{"source": "FINP Dev", "time": "${datetime_formatted}", "resources": ["Manual:invoke/LambdaCron-${env}-LambdaCronHourlyEvent-ZZZ"]}'
	aws lambda invoke --invocation-type Event --function-name LambdaCron-${env} \
    	--payload '{"source": "FINP Dev", "time": "${datetime_formatted}", "resources": ["Manual:invoke/LambdaCron-${env}-LambdaCronHourlyEvent-ABC"]}' \
    	/tmp/lambdaCron_invoke_output.txt

test:
	python -m pytest tests/

list:
	aws cloudformation list-stack-resources --stack-name $(cfn_stack) --region us-east-1

events:
	aws cloudformation describe-stack-events --stack-name $(cfn_stack) --region us-east-1

validate:
	aws cloudformation validate-template --template-body file://$(template) --region us-east-1

summary:
	aws cloudformation get-template-summary --stack-name $(cfn_stack) --region us-east-1

delete-stack:
	aws cloudformation delete-stack --stack-name $(cfn_stack)
	aws cloudformation wait stack-delete-complete --stack-name $(cfn_stack) --region us-east-1