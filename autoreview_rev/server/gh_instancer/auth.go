package gh_instancer

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"

	"github.com/google/uuid"
)

var states map[string]struct{} = map[string]struct{}{}
var stateMutex sync.RWMutex

type user struct {
	Login     string `json:"login"`
	Signature string `json:"sig"`
}

func (u *user) genSignature() string {
	h := hmac.New(sha256.New, []byte(os.Getenv("SECRET_KEY")))
	h.Write([]byte(u.Login))
	sig := h.Sum(nil)
	return hex.EncodeToString(sig)
}

func (u *user) genProjectId() string {
	h := hmac.New(sha256.New, []byte(os.Getenv("SECRET_KEY")))
	h.Write([]byte("PROJECT_ID"))
	h.Write([]byte(u.Login))
	sig := h.Sum(nil)
	return hex.EncodeToString(sig[:8])
}

func (u *user) verify() error {
	sig := u.genSignature()
	if sig != u.Signature {
		return fmt.Errorf("invalid signature")
	}
	return nil
}

func getAccessToken(code string) (accessToken string, err error) {
	clientId := os.Getenv("GH_APP_CLIENT_ID")
	clientSecret := os.Getenv("GH_APP_CLIENT_SECRET")
	body := fmt.Sprintf("client_id=%s&client_secret=%s&code=%s&redirect_uri=%s", clientId, clientSecret, code, os.Getenv("GH_APP_REDIRECT_URL"))
	req, err := http.NewRequest("POST", "https://github.com/login/oauth/access_token", strings.NewReader(body))
	if err != nil {
		err = fmt.Errorf("failed to create request: %v", err)
		return
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		err = fmt.Errorf("failed to get access token: %v", err)
		return
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		err = fmt.Errorf("failed to get access token: status code %v", resp.StatusCode)
		return
	}
	var tokenResponse struct {
		AccessToken string `json:"access_token"`
		Scope       string `json:"scope"`
		TokenType   string `json:"token_type"`
	}
	if err = json.NewDecoder(resp.Body).Decode(&tokenResponse); err != nil {
		err = fmt.Errorf("failed to decode access token response: %v", err)
		return
	}
	accessToken = tokenResponse.AccessToken
	return
}

func getUser(accessToken string) (u *user, err error) {
	req, err := http.NewRequest("GET", "https://api.github.com/user", nil)
	if err != nil {
		return
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)
	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return
	}

	var userResponse user

	err = json.NewDecoder(res.Body).Decode(&userResponse)
	if err != nil {
		return
	}

	userResponse.Signature = userResponse.genSignature()
	return &userResponse, nil
}

func getUserFromCookie(req *http.Request) *user {
	cookie, err := req.Cookie("user")
	if err != nil {
		return nil
	}
	cookieText, err := hex.DecodeString(cookie.Value)
	if err != nil {
		return nil
	}
	var u user
	err = json.Unmarshal(cookieText, &u)
	if err != nil {
		return nil
	}

	err = u.verify()
	if err != nil {
		return nil
	}

	return &u
}

func HandleAuth(w http.ResponseWriter, req *http.Request) {
	state := uuid.NewString()
	stateMutex.Lock()
	states[state] = struct{}{}
	stateMutex.Unlock()
	clientId := os.Getenv("GH_APP_CLIENT_ID")
	redirUrl := os.Getenv("GH_APP_REDIRECT_URL")
	http.Redirect(w, req, fmt.Sprintf("http://github.com/login/oauth/authorize?client_id=%s&redirect_url=%s&state=%s", clientId, redirUrl, state), http.StatusFound)
}

func HandleAuthCallback(w http.ResponseWriter, req *http.Request) {
	state := req.URL.Query().Get("state")
	stateMutex.RLock()
	_, ok := states[state]
	stateMutex.RUnlock()
	if !ok {
		http.Error(w, "invalid state", http.StatusBadRequest)
		return
	}
	stateMutex.Lock()
	delete(states, state)
	stateMutex.Unlock()

	code := req.URL.Query().Get("code")
	if code == "" {
		http.Error(w, "missing code", http.StatusBadRequest)
		return
	}

	accessToken, err := getAccessToken(code)

	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	user, err := getUser(accessToken)
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	userString, err := json.Marshal(user)
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	http.SetCookie(w, &http.Cookie{
		Name:     "user",
		Value:    hex.EncodeToString(userString),
		HttpOnly: true,
		Path:     "/",
	})
	http.Redirect(w, req, "/", http.StatusFound)
}
