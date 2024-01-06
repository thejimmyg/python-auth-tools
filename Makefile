.PHONY: clean deploy test check format deploy-lambda venv serve check-python

# ./serve/adapter/lambda_function/layer_from_requirements.sh "sudo -E docker" arm64 'cachetools==5.2.0 jwcrypto==1.0 pydantic==1.10.4 pysaml2==7.4.2 xmlsec==1.3.13' xmlsec-arm64.zip "yum update; yum install -y libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel"

venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt autoflake black mypy cfn-lint

deploy:
	@echo "Did you mean 'make deploy-lambda'?"

check-python:
	# Fails becauase of duplicate app_everything
	# .venv/bin/mypy --check-untyped-defs .

check: check-python
	.venv/bin/cfn-lint -i W3002 -- \
	  stack-deploy-lambda.template

test: clean check-python
	PATH="${PWD}:${PATH}" STORE_DIR=/tmp/store SAML_SP_SLACK_SECONDS='3' python3 test.py

format: format-python format-cfn

format-python:
	.venv/bin/autoflake -r --in-place --remove-unused-variables --remove-all-unused-imports . && .venv/bin/black .

format-cfn:
	cfn-format -w stack-* 

clean:
	rm -f lambda.zip index.py
	rm -rf /tmp/store ./test /tmp/tmp
	find . -type d  -name __pycache__ -print0 | xargs -0 rm -rf

lambda.zip: clean
	cp serve/adapter/lambda_function/index.py index.py
	zip --exclude '*/__pycache__/*' -r lambda.zip app serve kvstore *.py

deploy-check-env-aws:
ifndef AWS_REGION
	$(error AWS_REGION environment variable is undefined)
endif
ifndef AWS_ACCESS_KEY_ID
	$(error AWS_ACCESS_KEY_ID environment variable is undefined)
endif
ifndef AWS_SECRET_ACCESS_KEY
	$(error AWS_SECRET_ACCESS_KEY environment variable is undefined)
endif
ifndef AWS_SESSION_TOKEN
	$(error AWS_SESSION_TOKEN environment variable is undefined)
endif


deploy-check-env: deploy-check-env-aws
ifndef DOMAIN
	$(error DOMAIN environment variable is undefined)
endif
ifndef CLOUDFORMATION_BUCKET
	$(error CLOUDFORMATION_BUCKET environment variable is undefined)
endif
ifndef HOSTED_ZONE_ID
	$(error HOSTED_ZONE_ID environment variable is undefined)
endif
ifndef STACK_NAME
	$(error STACK_NAME environment variable is undefined)
endif
ifndef LAYERS
	$(error LAYERS environment variable is undefined)
endif
deploy-lambda: deploy-check-env clean check lambda.zip
	@echo "Deploying stack $(STACK_NAME) for https://$(DOMAIN) to $(AWS_REGION) via S3 bucket $(CLOUDFORMATION_BUCKET) using Route53 zone $(HOSTED_ZONE_ID)" ...
	aws cloudformation package \
	    --template-file "stack-deploy-lambda.template" \
	    --s3-bucket "${CLOUDFORMATION_BUCKET}" \
	    --s3-prefix "${STACK_NAME}" \
	    --output-template-file "deploy-lambda.yml" && \
	aws cloudformation deploy \
	    --template-file "deploy-lambda.yml" \
	    --stack-name "${STACK_NAME}" \
	    --capabilities CAPABILITY_NAMED_IAM \
	    --disable-rollback \
	    --parameter-overrides \
	        "Domain=${DOMAIN}" \
	        "HostedZoneId=${HOSTED_ZONE_ID}" \
	        "ReservedConcurrency=-1" \
	        "ThrottlingRateLimit=50" \
	        "ThrottlingBurstLimit=200" \
		"Layers=${LAYERS}"
