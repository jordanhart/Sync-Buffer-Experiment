package main

import (
	"fmt"
    "time"
	"github.com/zubairhamed/canopus"
	"encoding/json"
)

type time_tuple struct {
    psuedotime time.Duration
    data interface{}
}

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
    finish_timesync := time.Now()
    
	fmt.Println("offset in seconds : ")
	fmt.Println(offset.Seconds())
	fmt.Println("Time lapse: ")
	fmt.Println(finish_timesync.Sub(start))

	tok, err := conn.ObserveResource("/watch/this")
	if err != nil {
		panic(err.Error())
	}

	obsChannel := make(chan canopus.ObserveMessage)
	done := make(chan bool)
	go conn.Observe(obsChannel)

	notifyCount := 0
	go func() {
		for {
			select {
			case obsMsg, open := <-obsChannel:
				if open {
					if notifyCount == 5 {
						fmt.Println("[CLIENT >> ] Canceling observe after 5 notifications..")
						go conn.CancelObserveResource("watch/this", tok)
						go conn.StopObserve(obsChannel)
						done <- true
						return
					} else {
						notifyCount++
						// msg := obsMsg.Msg\
						resource := obsMsg.GetResource()
						val := obsMsg.GetValue()
						if str, ok := val.(string); ok { //trying to capture string json sent. TODO: Should change to send binary data for observe
                             var tuple time_tuple
                             json.Unmarshal([]byte(str), &tuple)
                             fmt.Println("tuple is: ", val)
                        } else {
                             /* not string */
                        	fmt.Println("[CLIENT >> ] Got Change Notification for resource and value: ", notifyCount, resource, val)
                        }


					}
				} else {
					done <- true
					return
				}
			}
		}
	}()
	<-done
	fmt.Println("Done")

}
