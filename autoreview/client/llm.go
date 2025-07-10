package client

import (
	"errors"
	"fmt"
	"os/exec"

	"jro.sg/auto-review/common"
)

var allowedCommands = map[string]struct{}{"cat": {}, "ls": {}, "go": {}}

func ExecTool(msg *common.ToolUseMessage) (res *common.ToolUseResponseMessage) {
	var err error
	defer func() {
		if err != nil {
			res = common.NewToolUseResponseMessage(msg.ID, err.Error(), true)
		}
	}()

	if len(msg.Command) > 2 {
		err = errors.New("command too long")
		return
	}
	if len(msg.Command) < 1 {
		err = errors.New("command too short")
		return
	}
	_, exists := allowedCommands[msg.Command[0]]
	if !exists {
		err = fmt.Errorf("you are not allowed to use %v", msg.Command[0])
		return
	}
	fmt.Println("Executing command", msg.Command)
	cmd := exec.Command(msg.Command[0], msg.Command[1])
	stdout, err := cmd.Output()
	if err != nil {
		return
	}
	return common.NewToolUseResponseMessage(msg.ID, string(stdout), false)
}
