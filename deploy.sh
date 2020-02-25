sam build --profile toastmxdev --use-container
sam package --profile toastmxdev --output-template-file packaged.yaml --s3-bucket brandline
sam deploy --profile toastmxdev --template-file packaged.yaml --capabilities CAPABILITY_IAM --stack-name brandline-admin-settings-apis