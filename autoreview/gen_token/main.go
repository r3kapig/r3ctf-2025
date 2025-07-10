package gen_token

import (
	"fmt"
	"os"

	"github.com/google/uuid"
	"jro.sg/auto-review/common"
)

func GenTokenMain() {
	projId := os.Getenv("PROJECT_ID")

	roomId := uuid.New()

	joinReq := common.NewJoinMessage(projId, roomId)

	fmt.Print(joinReq.ToToken())
}
