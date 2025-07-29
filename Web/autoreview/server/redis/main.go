package redis

import (
	"context"
	"os"
	"strconv"

	r "github.com/redis/go-redis/v9"
)

var redisClient *r.Client = nil

func GetClient() *r.Client {
	if redisClient != nil {
		return redisClient
	}
	redisClient = r.NewClient(&r.Options{
		Addr: os.Getenv("REDIS_ADDR"),
		DB:   0,
	})
	return redisClient
}

func CreateProject(ctx context.Context, projId string, owner string) error {
	rc := GetClient()
	_, err := rc.Set(ctx, "project_owner:"+projId, owner, 0).Result()
	if err != nil {
		return err
	}
	_, err = rc.Set(ctx, "project_tokens:"+projId, 0, 0).Result()
	if err != nil {
		return err
	}
	return nil
}

func ProjectExists(ctx context.Context, projId string) (bool, error) {
	rc := GetClient()
	val, err := rc.Exists(ctx, "project_owner:"+projId).Result()
	if err != nil {
		return false, err
	}
	return val > 0, nil
}

func GetProjectOwner(ctx context.Context, projId string) (string, error) {
	rc := GetClient()
	val, err := rc.Get(ctx, "project_owner:"+projId).Result()
	if err != nil {
		return "", err
	}
	return val, nil
}

func GetProjectTokenUsage(ctx context.Context, projId string) (int, error) {
	rc := GetClient()
	val, err := rc.Get(ctx, "project_tokens:"+projId).Result()
	if err != nil {
		return 0, err
	}
	intVal, err := strconv.Atoi(val)
	if err != nil {
		return 0, err
	}
	return intVal, nil
}

func SetProjectTokenUsage(ctx context.Context, projId string, usage int) error {
	rc := GetClient()
	_, err := rc.Set(ctx, "project_tokens:"+projId, usage, 0).Result()
	return err
}

func IncrementProjectTokenUsage(ctx context.Context, projId string, usage int) (int64, error) {
	rc := GetClient()
	return rc.IncrBy(ctx, "project_tokens:"+projId, int64(usage)).Result()
}

func DeleteKey(ctx context.Context, key string) error {
	rc := GetClient()
	return rc.Del(ctx, key).Err()
}
