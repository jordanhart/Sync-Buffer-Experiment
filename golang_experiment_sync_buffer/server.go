package main

import (
    "fmt"
    "time"
	"github.com/zubairhamed/canopus"
	"encoding/json"
	"math/rand"
	"strconv"
)

func main() {
	server := canopus.NewServer()
	psuedo_time_start := time.Now()

	// server.Get("/hello", func(req canopus.Request) canopus.Response {
	// 	log.Println("Hello Called")
	// 	msg := canopus.ContentMessage(req.GetMessage().GetMessageId(), canopus.MessageAcknowledgment)
	// 	msg.SetStringPayload("Acknowledged with response : " + req.GetMessage().GetPayload().String())

	// 	res := canopus.NewResponse(msg, nil)
	// 	return res
	// })

	// server.Post("/hello", func(req canopus.Request) canopus.Response {
	// 	log.Println("Hello Called via POST")

	// 	msg := canopus.ContentMessage(req.GetMessage().GetMessageId(), canopus.MessageAcknowledgment)
	// 	msg.SetStringPayload("Acknowledged: " + req.GetMessage().GetPayload().String())
	// 	res := canopus.NewResponse(msg, nil)
	// 	return res
	// })

	// server.Get("/basic", func(req canopus.Request) canopus.Response {
	// 	msg := canopus.NewMessageOfType(canopus.MessageAcknowledgment, req.GetMessage().GetMessageId(), canopus.NewPlainTextPayload("Acknowledged"))
	// 	res := canopus.NewResponse(msg, nil)
	// 	return res
	// })

	server.Get("/time", func(req canopus.Request) canopus.Response {
		now := time.Now()
        currentPsuedoTime  := now.Sub(psuedo_time_start)
		json_marshal, _ := json.Marshal(currentPsuedoTime)
		msg := canopus.ContentMessage(req.GetMessage().GetMessageId(), canopus.MessageAcknowledgment)
		msg.SetPayload(canopus.NewBytesPayload(json_marshal))
		res := canopus.NewResponse(msg, nil)
		return res
	})

	server.Get("/watch/this", func(req canopus.Request) canopus.Response {
		msg := canopus.NewMessageOfType(canopus.MessageAcknowledgment, req.GetMessage().GetMessageId(), canopus.NewPlainTextPayload("Acknowledged"))
		res := canopus.NewResponse(msg, nil)

		return res
	})
	ticker := time.NewTicker(3 * time.Second)
	go func() {
		for {
			select {
			case <-ticker.C:
				changeVal := strconv.Itoa(rand.Int())
				fmt.Println("[SERVER << ] Change of value -->", changeVal)

				server.NotifyChange("/watch/this", changeVal, false)
			}
		}
	}()

	// server.Get("/basic/json", func(req canopus.Request) canopus.Response {
	// 	msg := canopus.NewMessageOfType(canopus.MessageAcknowledgment, req.GetMessage().GetMessageId(), nil)

	// 	res := canopus.NewResponse(msg, nil)

	// 	return res
	// })

	// server.Get("/basic/xml", func(req canopus.Request) canopus.Response {
	// 	msg := canopus.NewMessageOfType(canopus.MessageAcknowledgment, req.GetMessage().GetMessageId(), nil)
	// 	res := canopus.NewResponse(msg, nil)

	// 	return res
	// })

	server.OnMessage(func(msg canopus.Message, inbound bool) {
		canopus.PrintMessage(msg)
	})

	server.OnObserve(func(resource string, msg canopus.Message) {
		fmt.Println("[SERVER << ] Observe Requested for " + resource)
	})

	server.ListenAndServe(":5683")
	<-make(chan struct{})
}
