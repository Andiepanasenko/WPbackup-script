# Consul catalog api actions

Function for api calls to consul catalog api.   
Please make sure consul is accessible for function.

## Makefile

Makefile is used only for development/debug/example purpose.  
Don`t use it for production. 

## Supported env variables

Consul variables: 

1. CONSUL_HTTP_ADDR
2. CONSUL_HTTP_TOKEN

Other variables see here: https://github.com/hashicorp/consul/blob/97b1d92c17fc29c7ac57490c22bfbc97c1127035/api/api.go#L27

Some defaults for Catalog Register:

1. SERVICE_PORT=80
2. NODE_NAME=external_node
3. NODE_ADDRESS=127.0.0.1

You can override them if needed.

## Supported actions 

1. Create
2. Delete

## Payload examples 

Create:
```json
{ 
  "service_name": "telegram_test_record", 
  "service_address" : "http://abc.com" 
}
```

Delete: 
```json
{ 
  "service_name": "telegram_test_record", 
  "service_address" : "http://abc.com", 
  "action" : "delete" 
}
```

## Lambda call example 

See Makefile for some examples
