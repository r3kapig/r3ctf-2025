package gh_instancer

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"os"
	"time"

	"github.com/google/go-github/v71/github"
	"golang.org/x/crypto/nacl/box"
)

func getClient(tokenId int) *github.Client {
	token1, exists1 := os.LookupEnv("ORG_OWNER_ACCESS_TOKEN_1")
	token2, exists2 := os.LookupEnv("ORG_OWNER_ACCESS_TOKEN_2")
	if tokenId == 1 || (tokenId == 0 && !exists2) {
		if !exists1 {
			return nil
		}
		return github.NewClient(nil).WithAuthToken(token1)
	}
	if tokenId == 2 || (tokenId == 0 && !exists1) {
		if !exists2 {
			return nil
		}
		return github.NewClient(nil).WithAuthToken(token2)
	}
	if time.Now().UnixMilli()%2 == 0 {
		return github.NewClient(nil).WithAuthToken(token1)
	} else {
		return github.NewClient(nil).WithAuthToken(token2)
	}
}

func getUsageMessage(ctx context.Context, c *github.Client) string {
	if c == nil {
		return "No token provided"
	}
	_, res, err := c.RateLimit.Get(ctx)
	if err != nil {
		return err.Error()
	}
	return fmt.Sprintln("Quota remaining:", res.Rate.Remaining, "reset at", res.Rate.Reset)
}

func newInstance(user *user, teamToken string) (*string, error) {
	targetRepoName := "auto-review-" + user.Login
	orgName := os.Getenv("ORG_NAME")
	repoUrl := fmt.Sprintf("https://github.com/%s/%s", orgName, targetRepoName)

	client := getClient(0)

	_, _, err := client.Repositories.Get(context.Background(), orgName, targetRepoName)
	if err == nil {
		_, err = client.Repositories.Delete(context.Background(), orgName, targetRepoName)
		if err != nil {
			return nil, fmt.Errorf("failed to delete existing repository: %w", err)
		}
	} else if _, ok := err.(*github.ErrorResponse); !ok {
		return nil, fmt.Errorf("failed to check existing repository: %w", err)
	}

	_, _, err = client.Repositories.CreateFromTemplate(context.Background(), orgName, "auto-review", &github.TemplateRepoRequest{
		Owner:              github.Ptr(orgName),
		Name:               github.Ptr(targetRepoName),
		Private:            github.Ptr(true),
		IncludeAllBranches: github.Ptr(true),
	})

	if err != nil {
		switch e := err.(type) {
		case *github.ErrorResponse:
			if e.Message != "Name already exists on this account" {
				return nil, err
			}
		case *github.AcceptedError:
		default:
			return nil, err
		}
	}

	projectId := user.genProjectId()

	_, _, err = client.Repositories.Edit(context.Background(), orgName, targetRepoName, &github.Repository{
		Description: github.Ptr("Fork this repository to start hacking! Project ID: " + projectId),
		HasIssues:   github.Ptr(true),
	})

	if err != nil {
		return nil, err
	}

	_, _, err = client.Repositories.AddCollaborator(context.Background(), orgName, targetRepoName, user.Login, &github.RepositoryAddCollaboratorOptions{
		Permission: "pull",
	})
	if err != nil {
		return nil, err
	}

	_, _, err = client.Repositories.EditActionsPermissions(context.Background(), orgName, targetRepoName, github.ActionsPermissionsRepository{
		Enabled:        github.Ptr(true),
		AllowedActions: github.Ptr("all"),
	})

	if err != nil {
		return nil, err
	}

	key, _, err := client.Actions.GetRepoPublicKey(context.Background(), orgName, targetRepoName)
	if err != nil {
		return nil, err
	}

	decodedPubKey, err := base64.StdEncoding.DecodeString(key.GetKey())
	if err != nil {
		return nil, err
	}

	out := []byte{}
	keyArr := [32]byte{}
	copy(keyArr[:], decodedPubKey)

	flag, err := user.genFlag(teamToken)
	if err != nil {
		return nil, err
	}

	encryptedBytes, err := box.SealAnonymous(out, []byte(flag), &keyArr, rand.Reader)
	if err != nil {
		return nil, fmt.Errorf("failed to encrypt secret")
	}
	_, err = client.Actions.CreateOrUpdateRepoSecret(context.Background(), orgName, targetRepoName, &github.EncryptedSecret{
		Name:           "flag",
		KeyID:          key.GetKeyID(),
		EncryptedValue: base64.StdEncoding.EncodeToString(encryptedBytes),
	})
	if err != nil {
		return nil, err
	}

	encryptedBytes, err = box.SealAnonymous(out, []byte(projectId), &keyArr, rand.Reader)
	if err != nil {
		return nil, fmt.Errorf("failed to encrypt secret")
	}
	_, err = client.Actions.CreateOrUpdateRepoSecret(context.Background(), orgName, targetRepoName, &github.EncryptedSecret{
		Name:           "project_id",
		KeyID:          key.GetKeyID(),
		EncryptedValue: base64.StdEncoding.EncodeToString(encryptedBytes),
	})
	return &repoUrl, err
}
