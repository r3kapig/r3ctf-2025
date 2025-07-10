package common

type InitMessage struct {
	MessageHeader
	ChangedFiles   []string `json:"changedFiles"`
	SupportedTools []string `json:"supportedTools"`
}

func NewInitMessage(changedFiles []string, supportedTools []string) *InitMessage {
	t := InitMessage{}
	t.MessageType = MessageTypeInit
	t.ChangedFiles = changedFiles
	t.SupportedTools = supportedTools
	return &t
}

type TextResponseMessage struct {
	MessageHeader
	Response string `json:"response"`
}

func NewTextResponseMessage(Response string) *TextResponseMessage {
	t := TextResponseMessage{}
	t.MessageType = MessageTypeTextResponse
	t.Response = Response
	return &t
}

type ToolUseMessage struct {
	MessageHeader
	ID      string   `json:"id"`
	Command []string `json:"cmd"`
}

func NewToolUseMessage(id string, command []string) *ToolUseMessage {
	t := ToolUseMessage{}
	t.MessageType = MessageTypeToolUse
	t.ID = id
	t.Command = command
	return &t
}

type ToolUseResponseMessage struct {
	MessageHeader
	ID      string `json:"id"`
	Result  string `json:"res"`
	IsError bool   `json:"isError"`
}

func NewToolUseResponseMessage(id string, result string, isError bool) *ToolUseResponseMessage {
	t := ToolUseResponseMessage{}
	t.MessageType = MessageTypeToolUseResponse
	t.ID = id
	t.Result = result
	t.IsError = isError
	return &t
}
