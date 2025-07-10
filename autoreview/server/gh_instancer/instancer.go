package gh_instancer

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"jro.sg/auto-review/server/redis"
)

func HandleNewInstance(w http.ResponseWriter, req *http.Request) {
	user := getUserFromCookie(req)
	if user == nil {
		http.Redirect(w, req, "/", http.StatusFound)
		return
	}

	teamToken := req.PostFormValue("team_token")
	if teamToken == "" {
		http.Error(w, "Team token is required", http.StatusBadRequest)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:  "team_token",
		Value: teamToken,
		Path:  "/",
	})

	client := redis.GetClient()
	keyExists, err := client.Exists(req.Context(), "created_project:"+user.Login).Result()
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if keyExists > 0 {
		http.Error(w, "Rate limit exceeded. Please try again later.", http.StatusTooManyRequests)
		return
	}

	url, err := newInstance(user, teamToken)
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = client.Set(req.Context(), "created_project:"+user.Login, 1, time.Minute*5).Err()
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	projId := user.genProjectId()

	exists, err := redis.ProjectExists(req.Context(), projId)
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if !exists {
		err = redis.CreateProject(req.Context(), projId, user.Login)
		if err != nil {
			log.Default().Println(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	http.Redirect(w, req, *url, http.StatusFound)
}

func HandleRepo(w http.ResponseWriter, req *http.Request) {
	u := getUserFromCookie(req)
	if u == nil {
		http.Redirect(w, req, "/", http.StatusFound)
		return
	}
	exists, err := redis.ProjectExists(req.Context(), u.genProjectId())
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if !exists {
		http.Redirect(w, req, "/", http.StatusFound)
		return
	}
	targetRepoName := "auto-review-" + u.Login
	orgName := os.Getenv("ORG_NAME")
	repoUrl := fmt.Sprintf("https://github.com/%s/%s", orgName, targetRepoName)

	http.Redirect(w, req, repoUrl, http.StatusFound)
}
