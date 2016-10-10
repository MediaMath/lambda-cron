cfn_stack   = LambdaCron-${env}
template    = template.cfn.yml
code_bucket = lambda-cron.${env}.mmknox
cur-dir     = $(shell pwd)
timestamp   = $(shell date +%s)
code_file   = code_$(timestamp).zip

list:
	aws cloudformation list-stack-resources --stack-name $(cfn_stack)

events:
	aws cloudformation describe-stack-events --stack-name $(cfn_stack)

delete-stack:
	aws cloudformation delete-stack --stack-name $(cfn_stack)

validate:
	aws cloudformation validate-template --template-body file://$(template)

summary:
	aws cloudformation get-template-summary --stack-name $(cfn_stack)

update-stack:
	aws cloudformation update-stack --stack-name $(cfn_stack) \
				--template-body file://$(template) \
				--parameters ParameterKey=CodeS3Key,UsePreviousValue=true \
					ParameterKey=Environment,ParameterValue=${env} \
					ParameterKey=State,ParameterValue=${state} \
				--capabilities CAPABILITY_NAMED_IAM

deploy:
	rm -f code.zip
	cd $(VIRTUAL_ENV)/lib/python2.7/site-packages; \
	zip --exclude=*pytest* --exclude=*boto3* -r $(cur-dir)/code.zip . --exclude=*pytest*
	zip code.zip main.py
	aws s3 cp code.zip s3://$(code_bucket)/code/${code_file}
	aws cloudformation update-stack --stack-name $(cfn_stack) \
				--template-body file://$(template) \
				--parameters ParameterKey=CodeS3Key,ParameterValue=code/$(code_file) \
					ParameterKey=Environment,ParameterValue=${env} \
					ParameterKey=State,ParameterValue=${state} \
				--capabilities CAPABILITY_NAMED_IAM

init:
	rm -f code.zip
	cd $(VIRTUAL_ENV)/lib/python2.7/site-packages; \
	zip --exclude=*pytest* --exclude=*boto3* -r $(cur-dir)/code.zip . --exclude=*pytest*
	zip code.zip main.py
	aws s3 cp code.zip s3://$(code_bucket)/code/${code_file}
	aws cloudformation create-stack --stack-name $(cfn_stack) \
				--template-body file://$(template) \
				--parameters ParameterKey=CodeS3Key,ParameterValue=code/$(code_file) \
					ParameterKey=Environment,ParameterValue=${env} \
					ParameterKey=State,ParameterValue=${state} \
				--capabilities CAPABILITY_NAMED_IAM
