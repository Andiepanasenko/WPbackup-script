package main

import (
	"fmt"
	"github.com/asaskevich/govalidator"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/hashicorp/consul/api"
	"github.com/kr/pretty"
	"log"
	"os"
	"strconv"
)

type UserEvent struct {
	ServiceName string `json:"service_name" valid:"required"`
	ServiceAddress string `json:"service_address" valid:"url,required"`
	Action string `json:"action"`
}

type Initials struct {
	NodeName string `json:"node_name"`
	NodeAddress string `json:"node_address"`
	ServiceId string `json:"service_id"`
	ServiceName string `json:"service_name"`
	ServiceAddress string `json:"service_address"`
	ServicePort int `json:"service_port"`
}

type LambdaResponse struct {
	Message string `json:"message:"`
	Error bool
}

var P Initials

func main() {
	lambda.Start(HandleLambdaEvent)
}

func init()  {
	port, _  := strconv.ParseInt(env("SERVICE_PORT", "80"), 10, 64)

	P = Initials{
		NodeName:       env("NODE_NAME", "external_node"),
		NodeAddress:    env("NODE_ADDRESS", "127.0.0.1"),
		ServicePort:    int(port),
	}

	d(P)
}

func HandleLambdaEvent(event UserEvent) (LambdaResponse, error) {
	ok, err := govalidator.ValidateStruct(event)

	if !ok {
		return LambdaResponse{
			Message: err.Error(),
			Error: true,
		}, nil
	}

	client, err := api.NewClient(api.DefaultConfig())

	if err != nil {
		return LambdaResponse{}, err
	}

	if event.Action == "delete" {
		services, _, err := client.Catalog().Service(event.ServiceName, "", nil)

		d("all services: ", services)

		if err != nil {
			return LambdaResponse{}, err
		}

		for _, s := range services {
			c := api.CatalogDeregistration{
				Node: s.Node,
				Address: s.ServiceAddress,
				ServiceID: s.ServiceID,
				Datacenter: s.Datacenter,
			}

			d("going to delete service: ", c)

			_, err := client.Catalog().Deregister(&c, nil);

			if err != nil {
				return LambdaResponse{}, err
			}
		}

		return LambdaResponse{
			Message: fmt.Sprintf("deleted %d rows", len(services)),
		}, nil
	} else { // create
		a := api.AgentService{
			ID: event.ServiceName,
			Service: event.ServiceName,
			Address: event.ServiceAddress,
			Port: P.ServicePort,
		}

		s := api.CatalogRegistration{
			Node:    P.NodeName,
			Address: P.NodeAddress,
			Service: &a,
			NodeMeta: map[string]string{
				"external-node" : "true",
				"external-probe" : "false",
			},
		}

		d("service to create: ", s)

		_, err := client.Catalog().Register(&s, nil)

		if err != nil {
			return LambdaResponse{}, err
		}

		services, _, err := client.Catalog().Service(event.ServiceName, "", nil)

		if err != nil {
			return LambdaResponse{}, err
		}

		return LambdaResponse{
			Message: fmt.Sprintf("service was created successfully; count: %d", len(services)),
		}, nil
	}
}

func env(key string, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		value = defaultValue
	}
	return value
}

func d(objs ...interface{})  {
	for _, obj := range objs {
		log.Printf("%# v\n", pretty.Formatter(obj))
	}
}
