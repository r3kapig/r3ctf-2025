package client

import (
	"fmt"
	"os/exec"
)

func updatePRComments(prNumber string, comment string) {
	cmd := exec.Command("gh", "pr", "comment", prNumber, "--body-file", "-")
	pipe, _ := cmd.StdinPipe()
	pipe.Write([]byte(comment))
	pipe.Close()
	stdout, _ := cmd.CombinedOutput()
	fmt.Print(string(stdout))
}
