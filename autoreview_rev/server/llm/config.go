package llm

import (
	"slices"

	"github.com/liushuangls/go-anthropic/v2"
	"jro.sg/auto-review/common"
)

type Config struct {
	toolUseHandler func(*common.ToolUseMessage)
	projectId      string
	initialMessage string
	supportedTools []string
}

func NewConfig(toolUseHandler func(*common.ToolUseMessage), projectId string, initialMessage string, supportedTools []string) *Config {
	return &Config{
		toolUseHandler: toolUseHandler,
		projectId:      projectId,
		initialMessage: initialMessage,
		supportedTools: supportedTools,
	}
}

func (c *Config) filterTools(tools []anthropic.ToolDefinition) []anthropic.ToolDefinition {
	filtered := []anthropic.ToolDefinition{}

	for _, tool := range tools {
		if slices.Contains(c.supportedTools, tool.Name) {
			filtered = append(filtered, tool)
		}
	}
	return filtered
}
