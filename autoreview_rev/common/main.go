package common

type MessageType uint

const (
	MessageTypeSuccess MessageType = iota
	MessageTypeError
	MessageTypeJoin
	MessageTypeInit
	MessageTypeTextResponse
	MessageTypeToolUse
	MessageTypeToolUseResponse
)

type MessageHeader struct {
	MessageType MessageType `json:"messageType"`
}

type Error struct {
	MessageHeader
	Message string `json:"message"`
}

func NewError(err error) *Error {
	e := Error{}
	e.MessageType = MessageTypeError
	e.Message = err.Error()
	return &e
}

type Success struct {
	MessageHeader
}

func NewSuccess() *Success {
	s := Success{}
	s.MessageType = MessageTypeSuccess
	return &s
}
