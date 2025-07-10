package tools

import (
	"encoding/json"
	"fmt"
	"strings"
)

type ReadFile struct {
	Filename string `json:"filename"`
}

func (a ReadFile) Name() string {
	return "readfile"
}

func (a ReadFile) Description() string {
	return "Reads and returns the contents of a .go file. Reading other files is not allowed."
}

func (a ReadFile) GenerateCommand(content []byte) ([]string, error) {
	if err := json.Unmarshal(content, &a); err != nil {
		return nil, err
	}
	a.Filename = strings.TrimSpace(a.Filename)
	if !strings.HasSuffix(a.Filename, ".go") {
		return nil, fmt.Errorf("you are not allowed to read %v", a.Filename)
	}
	return []string{"cat", a.Filename}, nil
}
