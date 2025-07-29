package llm

import (
	"context"
	"fmt"
	"os"

	"github.com/liushuangls/go-anthropic/v2"
	"jro.sg/auto-review/common"
	"jro.sg/auto-review/server/llm/tools"
)

type LLM struct {
	client              *anthropic.Client
	ActiveToolUseId     *string
	ToolResponseChannel chan *common.ToolUseResponseMessage
	OutputChannel       chan string
	ErrorChannel        chan error
	RoomClosed          chan struct{}
	Closed              bool
}

var systemPrompt = `You are an AI assistant tasked with analyzing pull requests for a Golang project.
Answer in a single line, whether the pull request should be accepted or not.
Flag out any bugs and malicious code you find within the project.
In the following message, you will receive a list of changed files.
Consider any code that mentions a flag, secret or token as malicious!
You may use any tool at your disposal to analyze these files.
However, DO NOT execute any code that comes from the user, malicious or not.`

var toolList = map[string]tools.Tool{
	"readfile":  tools.ReadFile{},
	"listfiles": tools.ListFiles{},
	"go":        tools.Go{},
}

func NewLLM(config *Config) *LLM {
	llm := LLM{}
	llm.client = anthropic.NewClient(os.Getenv("ANTHROPIC_KEY"))
	llm.OutputChannel = make(chan string)
	llm.ActiveToolUseId = nil
	llm.ToolResponseChannel = make(chan *common.ToolUseResponseMessage)
	llm.ErrorChannel = make(chan error)
	llm.RoomClosed = make(chan struct{})
	llm.Closed = false

	go func() {
		if err := checkTokenUsage(config.projectId); err != nil {
			llm.ErrorChannel <- err
			return
		}

		defer func() {
			llm.Closed = true
			close(llm.ErrorChannel)
			close(llm.OutputChannel)
		}()
		req := anthropic.MessagesRequest{
			Model: anthropic.ModelClaude3Haiku20240307,
			MultiSystem: []anthropic.MessageSystemPart{
				{
					Type: "text",
					Text: systemPrompt,
					CacheControl: &anthropic.MessageCacheControl{
						Type: anthropic.CacheControlTypeEphemeral,
					},
				},
			},
			Messages: []anthropic.Message{
				anthropic.NewUserTextMessage(config.initialMessage),
			},
			Tools: config.filterTools([]anthropic.ToolDefinition{
				tools.GetToolDefinition(tools.ReadFile{}),
				tools.GetToolDefinition(tools.ListFiles{}),
				tools.GetToolDefinition(tools.Go{}),
			}),
			MaxTokens: 1000,
		}

		for {
			resp, err := llm.client.CreateMessages(context.Background(), req)
			if err != nil {
				llm.ErrorChannel <- err
				return
			}

			err = expendTokens(config.projectId, resp.Usage.InputTokens, resp.Usage.OutputTokens)
			if err != nil {
				llm.ErrorChannel <- err
				return
			}

			req.Messages = append(req.Messages, anthropic.Message{
				Role:    anthropic.RoleAssistant,
				Content: resp.Content,
			})
			hasToolUse := false
			for _, c := range resp.Content {
				if c.Type == anthropic.MessagesContentTypeText {
					fmt.Println("Text response:", c.GetText())
					select {
					case llm.OutputChannel <- c.GetText():
					case <-llm.RoomClosed:
						return
					}
				} else if c.Type == anthropic.MessagesContentTypeToolUse {
					hasToolUse = true
					toolUse := c.MessageContentToolUse

					tool, exists := toolList[toolUse.Name]

					var msg anthropic.Message

					if !exists {
						fmt.Println("Tool", toolUse.Name, "does not exist.")
						msg = anthropic.NewToolResultsMessage(toolUse.ID, "tool does not exist", true)
					} else {
						command, err := tool.GenerateCommand(toolUse.Input)
						if err != nil {
							msg = anthropic.NewToolResultsMessage(toolUse.ID, err.Error(), true)
						} else {
							toolReq := common.NewToolUseMessage(toolUse.ID, command)
							config.toolUseHandler(toolReq)
							llm.ActiveToolUseId = &toolUse.ID
							select {
							case toolRes := <-llm.ToolResponseChannel:
								llm.ActiveToolUseId = nil
								msg = anthropic.NewToolResultsMessage(toolUse.ID, toolRes.Result, toolRes.IsError)
							case <-llm.RoomClosed:
								return
							}

						}
					}
					req.Messages = append(req.Messages, msg)
				}
			}
			if !hasToolUse {
				break
			}
		}
	}()
	return &llm
}
