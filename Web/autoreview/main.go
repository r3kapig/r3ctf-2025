package main

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
	"jro.sg/auto-review/client"
	"jro.sg/auto-review/gen_token"
	"jro.sg/auto-review/server"
)

func main() {
	godotenv.Load()
	if len(os.Args) < 2 {
		fmt.Println("Please specify client, server or gen_token")
		return
	}
	if os.Args[1] == "client" {
		client.ClientMain()
	} else if os.Args[1] == "server" {
		server.ServerMain()
	} else if os.Args[1] == "gen_token" {
		gen_token.GenTokenMain()
	} else {
		fmt.Printf("Please specify client, server or gen_token, not %v", os.Args[1])
	}
}
