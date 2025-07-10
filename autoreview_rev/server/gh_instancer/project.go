package gh_instancer

import (
	"fmt"
	"log"
	"net/http"

	"jro.sg/auto-review/server/redis"
)

func HandleGetMyProject(w http.ResponseWriter, r *http.Request) {
	u := getUserFromCookie(r)
	if u == nil {
		http.Redirect(w, r, "/", http.StatusFound)
		return
	}
	projId := u.genProjectId()
	owner, err := redis.GetProjectOwner(r.Context(), projId)
	if err != nil {
		http.Redirect(w, r, "/", http.StatusFound)
		return
	}
	tokenUsage, err := redis.GetProjectTokenUsage(r.Context(), projId)
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "Project %v is owned by %v, %v tokens expended", projId, owner, tokenUsage)
}

func HandleResetProjectUsage(w http.ResponseWriter, r *http.Request) {
	projId := r.PathValue("projId")
	err := redis.SetProjectTokenUsage(r.Context(), projId, 0)
	if err != nil {
		http.Error(w, "invalid project id", http.StatusBadRequest)
		return
	}

	fmt.Fprintf(w, "token count for project %v reset successfully", projId)
}
