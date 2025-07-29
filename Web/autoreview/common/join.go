package common

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"strings"

	"github.com/google/uuid"
)

type JoinMessage struct {
	MessageHeader
	ProjectId string    `json:"projectId"`
	RoomId    uuid.UUID `json:"roomId"`
	Signature string    `json:"signature"`
}

func NewJoinMessage(projectId string, roomId uuid.UUID) *JoinMessage {
	msg := JoinMessage{}
	msg.ProjectId = projectId
	msg.MessageType = MessageTypeJoin
	msg.RoomId = roomId
	msg.Signature = msg.genSignature()
	return &msg
}

func (msg *JoinMessage) genSignature() string {
	flag := os.Getenv("FLAG")
	if len(flag) < 32 {
		panic("$FLAG must be at least 32 bytes long!")
	}
	flag = flag[:32]
	h := hmac.New(sha256.New, []byte(flag))
	h.Write([]byte(msg.ProjectId))
	h.Write(msg.RoomId[:])
	return hex.EncodeToString(h.Sum(nil))
}

func (msg *JoinMessage) Verify() error {
	if msg.Signature != msg.genSignature() {
		return errors.New("invalid signature")
	}
	return nil
}

func (msg *JoinMessage) ToToken() string {
	return fmt.Sprintf("%s.%s.%s", msg.ProjectId, msg.RoomId, msg.genSignature())
}

func NewJoinMessageFromToken(token string) *JoinMessage {
	msg := JoinMessage{}
	msg.MessageType = MessageTypeJoin
	parts := strings.SplitN(token, ".", 3)
	if len(parts) != 3 {
		panic("Malformed token!")
	}
	msg.ProjectId = parts[0]
	msg.RoomId = uuid.MustParse(parts[1])
	msg.Signature = parts[2]
	return &msg
}
