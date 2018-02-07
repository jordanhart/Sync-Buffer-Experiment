package main

import (
	"fmt"
    "time"
	"github.com/zubairhamed/canopus"
	"encoding/json"
)

func main() {
	start := time.Now()
	fmt.Println("Connecting to CoAP Server")
	conn, err := canopus.Dial("localhost:5683")
	if err != nil {
		panic(err.Error())
	}
	req := canopus.NewRequest(canopus.MessageConfirmable, canopus.Get)
	req.SetStringPayload("")
	req.SetRequestURI("/time")

	fmt.Println("Sending request..")
	resp, err := conn.Send(req)
	if err != nil {
		panic(err.Error())
	}
	psuedotime_string := resp.GetMessage().GetPayload().GetBytes()
    var offset time.Duration
	json.Unmarshal(psuedotime_string, &offset)
	// t := time.Microsecond
    finish := time.Now()
    
	fmt.Println("offset in seconds : ")
	fmt.Println(offset.Seconds())
	fmt.Println("Time lapse: ")
	fmt.Println(finish.Sub(start))

}
