package ws

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"jro.sg/auto-review/common"
)

var rooms = map[uuid.UUID]*Room{}
var roomsMutex = sync.RWMutex{}

type wsConn struct {
	c  *websocket.Conn
	mu sync.Mutex
}

func NewWsConn(c *websocket.Conn) *wsConn {
	return &wsConn{
		c:  c,
		mu: sync.Mutex{},
	}
}
func (w *wsConn) send(v interface{}) error {
	w.mu.Lock()
	defer w.mu.Unlock()
	return w.c.WriteJSON(v)
}

func Handle(_conn *websocket.Conn) {
	var msgHdr common.MessageHeader
	var err error
	var resp any
	joinedRoom := uuid.Nil
	conn := NewWsConn(_conn)

	done := make(chan struct{})

	go func() {
		select {
		case <-time.After(time.Minute):
			conn.c.Close()
		case <-done:
		}
	}()

	defer func() {
		close(done)
		roomsMutex.Lock()
		room := rooms[joinedRoom]
		if room != nil {
			room.Remove(conn)
			room.membersMutex.Lock()
			membersCount := len(room.members)
			room.membersMutex.Unlock()
			if membersCount == 0 {
				fmt.Println("Closing room", joinedRoom)
				delete(rooms, joinedRoom)
				roomsMutex.Unlock()
				if room.llm != nil && !room.llm.Closed {
					close(room.llm.RoomClosed)
				}
			} else {
				roomsMutex.Unlock()
			}
		} else {
			roomsMutex.Unlock()
		}

		if err != nil {
			if _, ok := err.(*websocket.CloseError); ok {
				return
			}

			if _, ok := err.(net.Error); ok {
				return
			}

			fmt.Println("Closed connection with error", err.Error())
			conn.send(common.NewError(err))
		}
	}()

	for {
		mt, message, _err := conn.c.ReadMessage()
		err = _err
		if err != nil {
			break
		}
		if mt != websocket.TextMessage {
			break
		}
		err = json.Unmarshal(message, &msgHdr)
		if err != nil {
			break
		}
		switch msgHdr.MessageType {
		case common.MessageTypeJoin:
			if joinedRoom != uuid.Nil {
				err = errors.New("cannot join more than one room")
				return
			}
			var joinMessage common.JoinMessage
			err = json.Unmarshal(message, &joinMessage)
			if err != nil {
				return
			}
			resp, err = handleJoin(&joinMessage, conn)
			if err == nil {
				joinedRoom = joinMessage.RoomId
			} else {
				return
			}
		case common.MessageTypeInit:
			if joinedRoom == uuid.Nil {
				err = errors.New("please join a room first")
				return
			}
			roomsMutex.RLock()
			room := rooms[joinedRoom]
			roomsMutex.RUnlock()
			var initMessage common.InitMessage
			err = json.Unmarshal(message, &initMessage)
			if err != nil {
				return
			}
			resp, err = room.HandleInit(initMessage)
		case common.MessageTypeToolUseResponse:
			if joinedRoom == uuid.Nil {
				err = errors.New("please join a room first")
				return
			}
			roomsMutex.RLock()
			room := rooms[joinedRoom]
			roomsMutex.RUnlock()
			var toolUseResponse common.ToolUseResponseMessage
			err = json.Unmarshal(message, &toolUseResponse)
			if err != nil {
				return
			}
			resp, err = room.HandleToolUseResponse(toolUseResponse)
		}
		err = conn.send(resp)
		if err != nil {
			log.Println("write:", err)
			break
		}
	}
}
