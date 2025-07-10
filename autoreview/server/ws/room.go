package ws

import (
	"errors"
	"fmt"
	"sync"

	"jro.sg/auto-review/common"
	"jro.sg/auto-review/server/llm"
)

type Room struct {
	projectId    string
	members      map[*wsConn]struct{}
	llm          *llm.LLM
	membersMutex sync.RWMutex
}

func NewRoom(projectId string) *Room {
	r := Room{}
	r.projectId = projectId
	r.members = make(map[*wsConn]struct{})
	r.llm = nil
	return &r
}

func (r *Room) HandleInit(msg common.InitMessage) (*common.Success, error) {
	if r.llm != nil {
		return nil, errors.New("llm already initialized")
	}

	initialMessage := "List of changed files:\n"
	for _, file := range msg.ChangedFiles {
		initialMessage += fmt.Sprintf("- %s\n", file)
	}

	config := llm.NewConfig(r.BroadcastToolUseRequest, r.projectId, initialMessage, msg.SupportedTools)
	r.llm = llm.NewLLM(config)
	go func() {
		for {
			select {
			case out := <-r.llm.OutputChannel:
				msg := common.NewTextResponseMessage(out)
				r.membersMutex.Lock()
				for m := range r.members {
					err := m.send(msg)
					if err != nil {
						r.Remove(m)
						m.c.Close()
					}
				}
				r.membersMutex.Unlock()
			case err := <-r.llm.ErrorChannel:
				msg := common.NewTextResponseMessage(fmt.Sprintf("An error has occurred: %v", err))
				r.membersMutex.Lock()
				for m := range r.members {
					m.send(msg)
					r.Remove(m)
					m.c.Close()
				}
				r.membersMutex.Unlock()
				return
			}
		}
	}()
	return common.NewSuccess(), nil
}

func (r *Room) HandleToolUseResponse(msg common.ToolUseResponseMessage) (*common.Success, error) {
	if r.llm.ActiveToolUseId != nil && msg.ID == *r.llm.ActiveToolUseId {
		r.llm.ToolResponseChannel <- &msg
	} else {
		fmt.Printf("Discarding duplicate tool response %+v\n", msg)
	}
	return common.NewSuccess(), nil
}

func (r *Room) BroadcastToolUseRequest(req *common.ToolUseMessage) {
	r.membersMutex.Lock()
	for conn := range r.members {
		err := conn.send(req)
		if err != nil {
			r.Remove(conn)
		}
	}
	r.membersMutex.Unlock()
}

func (r *Room) Remove(conn *wsConn) {
	delete(r.members, conn)
}
