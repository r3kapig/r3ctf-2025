package client

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"strings"

	"github.com/gorilla/websocket"
	"jro.sg/auto-review/common"
)

type incomingMessage struct {
	msgType common.MessageType
	message []byte
}

func recvuntil(c <-chan *incomingMessage, msgType common.MessageType) []byte {
	for msg := range c {
		if msg.msgType == msgType {
			return msg.message
		}
	}
	panic("message not found")
}

func unmarshalOrPanic[T any](data []byte) *T {
	var res T
	err := json.Unmarshal(data, &res)
	if err != nil {
		panic(err)
	}
	return &res
}

func createReceiveChannel(conn *websocket.Conn) chan *incomingMessage {
	c := make(chan *incomingMessage)
	go func() {
		for {
			mt, message, err := conn.ReadMessage()
			if err != nil {
				panic(err)
			}
			if mt != websocket.TextMessage {
				break
			}
			msgHdr := unmarshalOrPanic[common.MessageHeader](message)
			if msgHdr.MessageType == common.MessageTypeError {
				wsError := unmarshalOrPanic[common.Error](message)
				panic(wsError.Message)
			}
			msg := incomingMessage{
				msgType: msgHdr.MessageType,
				message: message,
			}
			c <- &msg
		}
	}()
	return c
}

func ClientMain() error {
	url := "ws://localhost:8080/ws"

	if u, ok := os.LookupEnv("SERVER_ADDR"); ok {
		url = u
	}

	token := os.Getenv("TOKEN")

	joinReq := common.NewJoinMessageFromToken(token)

	baseCommit := "main"
	if b, ok := os.LookupEnv("BASE_SHA"); ok {
		baseCommit = b
	}

	changedFilesList := exec.Command("git", "diff", "--name-only", baseCommit, "-r")

	_stdout, err := changedFilesList.Output()
	if err != nil {
		panic(err)
	}

	stdout := string(_stdout)

	fmt.Println("Changed files:", stdout)

	conn, _, err := websocket.DefaultDialer.Dial(url, nil)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	recvChannel := createReceiveChannel(conn)

	conn.WriteJSON(joinReq)
	recvuntil(recvChannel, common.MessageTypeSuccess)
	fmt.Println("Join success")

	files := strings.Split(stdout, "\n")

	for _, file := range files {
		stat, err := os.Lstat(file)
		if err != nil {
			panic(err)
		}
		if stat.Mode()&fs.ModeSymlink != 0 {
			panic("Symlink detected!")
		}
	}

	conn.WriteJSON(common.NewInitMessage(files, []string{"readfile", "listfiles"}))
	recvuntil(recvChannel, common.MessageTypeSuccess)
	fmt.Println("Prompt sent")

	for msg := range recvChannel {
		switch msg.msgType {
		case common.MessageTypeTextResponse:
			textResponse := unmarshalOrPanic[common.TextResponseMessage](msg.message)
			if len(textResponse.Response) > 0 {
				fmt.Println("Text response:", textResponse.Response)
				prNumber := os.Getenv("PR_NUMBER")
				if len(prNumber) > 0 {
					updatePRComments(prNumber, textResponse.Response)
				} else {
					fmt.Println("Skipping PR comment update as PR_NUMBER is not defined.")
				}
				return nil
			}
		case common.MessageTypeToolUse:
			toolUse := unmarshalOrPanic[common.ToolUseMessage](msg.message)
			res := ExecTool(toolUse)
			conn.WriteJSON(res)
		case common.MessageTypeSuccess:

		default:
			fmt.Println("Unhandled message:", string(msg.message))
		}
	}

	return nil
}
