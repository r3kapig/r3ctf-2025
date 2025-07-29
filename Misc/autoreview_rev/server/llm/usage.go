package llm

import (
	"context"
	"errors"
	"fmt"

	"jro.sg/auto-review/server/redis"
)

// Should be enough for about 200 requests and cost 5 cents
var totalTokenLimit int64 = 200_000

var errTokenLimit = errors.New("token limit exceeded. contact admins for token limit reset")

func expendTokens(projId string, numIn int, numOut int) error {
	tokens := int64(numIn)
	tokens += int64(numOut) * 5
	tokens, err := redis.IncrementProjectTokenUsage(context.Background(), projId, int(tokens))
	if err != nil {
		return err
	}
	fmt.Println("Expended", tokens, "tokens")
	fmt.Printf("Total cost: %.6f cents\n", float64(tokens*25)/1_000_000)
	if tokens >= totalTokenLimit {
		return errTokenLimit
	}
	return nil
}

func checkTokenUsage(projId string) error {
	tokens, err := redis.GetProjectTokenUsage(context.Background(), projId)
	if err != nil {
		return err
	}
	if int64(tokens) >= totalTokenLimit {
		return errTokenLimit
	}
	return nil
}
