package server

import (
	"crypto/sha256"
	"crypto/subtle"
	"log"
	"net/http"
	"os"

	"time"

	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
	"github.com/ulule/limiter/v3"
	"jro.sg/auto-review/server/gh_instancer"
	"jro.sg/auto-review/server/ws"

	mhttp "github.com/ulule/limiter/v3/drivers/middleware/stdlib"

	lr "github.com/ulule/limiter/v3/drivers/store/redis"
	"jro.sg/auto-review/server/redis"
)

var upgrader = websocket.Upgrader{}

func wsHandler(w http.ResponseWriter, r *http.Request) {
	c, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("upgrade:", err)
		return
	}
	defer c.Close()
	ws.Handle(c)
}

func basicAuth(next func(w http.ResponseWriter, r *http.Request)) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		_, password, ok := r.BasicAuth()
		if ok {
			passwordHash := sha256.Sum256([]byte(password))
			expectedPasswordHash := sha256.Sum256([]byte(os.Getenv("SECRET_KEY")))
			passwordMatch := (subtle.ConstantTimeCompare(passwordHash[:], expectedPasswordHash[:]) == 1)

			if passwordMatch {
				next(w, r)
				return
			}
		}

		w.Header().Set("WWW-Authenticate", `Basic realm="restricted", charset="UTF-8"`)
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
	}
}

func newLimiterMiddleware(id string, limit limiter.Rate) *mhttp.Middleware {
	store, err := lr.NewStoreWithOptions(redis.GetClient(), limiter.StoreOptions{
		Prefix: "limiter_" + id,
	})

	if err != nil {
		panic(err)
	}

	return mhttp.NewMiddleware(
		limiter.New(store, limit),
	)
}

func ServerMain() {
	godotenv.Load()

	http.HandleFunc("GET /{$}", gh_instancer.HandleFrontPage)

	http.Handle("POST /newInstance", newLimiterMiddleware("instancer", limiter.Rate{
		Period: time.Minute * 30,
		Limit:  5,
	}).Handler(http.HandlerFunc(gh_instancer.HandleNewInstance)))

	http.HandleFunc("GET /repo", gh_instancer.HandleRepo)

	http.HandleFunc("GET /auth", gh_instancer.HandleAuth)
	http.Handle("GET /auth/callback", newLimiterMiddleware("auth_callback", limiter.Rate{
		Period: time.Minute * 30,
		Limit:  10,
	}).Handler(http.HandlerFunc(gh_instancer.HandleAuthCallback)))

	http.HandleFunc("GET /project", gh_instancer.HandleGetMyProject)
	http.HandleFunc("GET /admin/stats", basicAuth(gh_instancer.HandleStats))
	http.HandleFunc("GET /admin/limits", basicAuth(gh_instancer.HandleRateLimitStats))
	http.HandleFunc("POST /admin/projects/{projId}/usage/reset", basicAuth(gh_instancer.HandleResetProjectUsage))
	http.HandleFunc("POST /admin/reset", basicAuth(gh_instancer.HandleReset))

	http.HandleFunc("/ws", wsHandler)
	http.ListenAndServe(":8080", nil)
}
