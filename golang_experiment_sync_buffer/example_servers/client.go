package main

import (
	"fmt"
    "time"
	"github.com/zubairhamed/canopus"
)

func main() {
	start := time.Now()
	fmt.Println("Connecting to CoAP Server")
	conn, err := canopus.Dial("localhost:5683")
	if err != nil {
		panic(err.Error())
	}
	req := canopus.NewRequest(canopus.MessageConfirmable, canopus.Get)
	req.SetStringPayload("Hello, canopus")
	req.SetRequestURI("/hello")

	fmt.Println("Sending request..")
	resp, err := conn.Send(req)
	if err != nil {
		panic(err.Error())
	}
    finish := time.Now()
	fmt.Println("Got Response:" + resp.GetMessage().GetPayload().String())
	fmt.Println("Time lapse: ")
	fmt.Println(finish.Sub(start))

}
