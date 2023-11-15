.PHONY: clean deploy test check format deploy-lambda venv serve

venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt isort autoflake black mypy cfn-lint

deploy:
	@echo "Did you mean 'make deploy-lambda'?"

check:
	# .venv/bin/mypy --check-untyped-defs .
	.venv/bin/cfn-lint -i W3002 -- \
	  stack-deploy-lambda.template

test: clean
	PATH="${PWD}:${PATH}" STORE_DIR=store SAML_SP_SLACK_SECONDS='3' python3 test.py cli_serve_wsgi.py

format: format-python format-cfn

format-python:
	.venv/bin/isort . && .venv/bin/autoflake -r --in-place --remove-unused-variables --remove-all-unused-imports . && .venv/bin/black .

format-cfn:
	cfn-format -w stack-* 

clean:
	rm -f lambda.zip
	rm -rf ./store ./test ./tmp
	find . -type d  -name __pycache__ -print0 | xargs -0 rm -rf

lambda.zip: clean
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
