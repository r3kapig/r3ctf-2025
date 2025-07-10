package tools

import (
	"encoding/json"
)

type Go struct {
	Command string `json:"cmd"`
}

func (a Go) Name() string {
	return "go"
}

func (a Go) Description() string {
	return "Runs a go command. The go command must not have any arguments, eg `go build`."
}

func (a Go) GenerateCommand(content []byte) ([]string, error) {
	if err := json.Unmarshal(content, &a); err != nil {
		return nil, err
	}
	return []string{"go", a.Command}, nil
}
