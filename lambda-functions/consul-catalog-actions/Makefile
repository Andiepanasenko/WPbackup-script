build:
	GOOS=linux go build -o main main.go

upload:
	zip -FSr lambda.zip main \
    && aws lambda update-function-code --function-name gofunc1 --zip-file fileb://./lambda.zip \
    && rm lambda.zip && rm main

deploy:
	make build && make upload

delete:
	aws lambda invoke --function-name gofunc1 \
    --cli-binary-format raw-in-base64-out \
	--payload '{ "service_name": "as-stage-telegram-notification-addon", "service_address" : "http://telegram-notification-addon.as-stage.int", "action" : "delete" }' response.json && cat response.json | jq && rm response.json

create:
	aws lambda invoke --function-name gofunc1 \
    --cli-binary-format raw-in-base64-out \
	--payload '{ "service_name": "as-stage-telegram-notification-addon", "service_address" : "http://telegram-notification-addon.as-stage.int" }' response.json && cat response.json | jq && rm response.json

delete-v1:
	aws lambda invoke --function-name gofunc1 \
	--payload '{ "service_name": "as-stage-telegram-notification-addon", "service_address" : "http://telegram-notification-addon.as-stage.int", "action" : "delete" }' response.json && cat response.json | jq && rm response.json

create-v1:
	aws lambda invoke --function-name gofunc1 \
	--payload '{ "service_name": "as-stage-telegram-notification-addon", "service_address" : "http://telegram-notification-addon.as-stage.int" }' response.json && cat response.json | jq && rm response.json