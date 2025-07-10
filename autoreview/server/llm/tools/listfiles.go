package tools

import (
	"encoding/json"
	"strings"
)

type ListFiles struct {
	Dirname string `json:"dirname"`
}

func (a ListFiles) Name() string {
	return "listfiles"
}

func (a ListFiles) Description() string {
	return "Lists contents of a directory."
}

func (a ListFiles) GenerateCommand(content []byte) ([]string, error) {
	if err := json.Unmarshal(content, &a); err != nil {
		return nil, err
	}
	a.Dirname = strings.TrimSpace(a.Dirname)
	return []string{"ls", a.Dirname}, nil
}
