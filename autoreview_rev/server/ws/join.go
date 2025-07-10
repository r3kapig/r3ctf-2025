package ws

import (
	"context"
	"fmt"

	"jro.sg/auto-review/common"
	"jro.sg/auto-review/server/redis"
)

func handleJoin(msg *common.JoinMessage, conn *wsConn) (resp *common.Success, err error) {
	roomId := msg.RoomId
	err = msg.Verify()
	if err != nil {
		return
	}
	roomsMutex.Lock()
	defer roomsMutex.Unlock()
	_, exists := rooms[roomId]
	if !exists {
		exists, err = redis.ProjectExists(context.Background(), msg.ProjectId)
		if err != nil {
			return
		}
		if !exists {
			return nil, fmt.Errorf("project %v does not exist", msg.ProjectId)
		}
		fmt.Println("Creating room", roomId, "with project id", msg.ProjectId)
		rooms[roomId] = NewRoom(msg.ProjectId)
	}
	rooms[roomId].membersMutex.Lock()
	rooms[roomId].members[conn] = struct{}{}
	rooms[roomId].membersMutex.Unlock()
	resp = common.NewSuccess()
	return
}
