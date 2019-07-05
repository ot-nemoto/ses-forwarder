deploy_bucket_stack_name = ses-forwarder-bucket-stack
sam_stack_name = ses-forwarder-stack
make = make --no-print-directory

domain = mail.example.com
source_user = ''
forwarder = ''
forwarding_address = recept_to@mail.example.com

create-deploy-bucket-stack:
ifneq ($(shell aws cloudformation describe-stacks \
  --query 'Stacks[?StackName==`${deploy_bucket_stack_name}`].StackName' \
  --output text 2>/dev/null), ${deploy_bucket_stack_name})
	aws cloudformation create-stack --stack-name $(deploy_bucket_stack_name) --template-body file://bucket-template.yaml
	aws cloudformation wait stack-create-complete --stack-name $(deploy_bucket_stack_name)
endif

deploy: create-deploy-bucket-stack
	$(eval bucket := $(shell aws cloudformation describe-stacks \
	  --stack-name ${deploy_bucket_stack_name} \
	  --query 'Stacks[].Outputs[?OutputKey==`S3Bucket`].OutputValue' \
	  --output text))
	sam package --s3-bucket $(bucket) --output-template-file packaged.yml
	sam deploy --template-file packaged.yml --stack-name $(sam_stack_name) --capabilities CAPABILITY_IAM \
	  --parameter-overrides Domain=$(domain) \
                                SourceUser=$(source_user) \
                                Forwarder=$(forwarder) \
                                ForwardingAddress=$(forwarding_address)
	@$(make) enable_active_rule_set

enable_active_rule_set:
	$(eval rule_set := $(shell aws cloudformation describe-stacks \
	  --stack-name ${sam_stack_name} \
	  --query 'Stacks[].Outputs[?OutputKey==`RuleSet`].OutputValue' \
	  --output text))
	aws ses set-active-receipt-rule-set --rule-set-name $(rule_set)

disable_active_rule_set:
	aws ses set-active-receipt-rule-set

remove-received-mail:
ifeq ($(shell aws cloudformation describe-stacks \
  --query 'Stacks[?StackName==`${sam_stack_name}`].StackName' \
  --output text 2>/dev/null), ${sam_stack_name})
	$(eval bucket := $(shell aws cloudformation describe-stacks\
	  --stack-name ${sam_stack_name}\
	  --query 'Stacks[].Outputs[?OutputKey==`S3Bucket`].OutputValue'\
	  --output text))
	aws s3 rm s3://$(bucket) --recursive
endif

undeploy:
	@$(make) remove-received-mail
	@$(make) disable_active_rule_set
	aws cloudformation delete-stack --stack-name $(sam_stack_name)
	aws cloudformation wait stack-delete-complete --stack-name $(sam_stack_name)

remove-deploy-bucket-packages:
ifeq ($(shell aws cloudformation describe-stacks \
  --query 'Stacks[?StackName==`${deploy_bucket_stack_name}`].StackName' \
  --output text 2>/dev/null), ${deploy_bucket_stack_name})
	$(eval bucket := $(shell aws cloudformation describe-stacks\
	  --stack-name ${deploy_bucket_stack_name}\
	  --query 'Stacks[].Outputs[?OutputKey==`S3Bucket`].OutputValue'\
	  --output text))
	aws s3 rm s3://$(bucket) --recursive
endif

delete-deploy-bucket-stack: remove-deploy-bucket-packages
	aws cloudformation delete-stack --stack-name $(deploy_bucket_stack_name)
	aws cloudformation wait stack-delete-complete --stack-name $(deploy_bucket_stack_name)

delete:
	@$(make) undeploy
	@$(make) delete-deploy-bucket-stack
