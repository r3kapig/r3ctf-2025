package gh_instancer

import (
	"fmt"
	"html/template"
	"log"
	"net/http"

	"jro.sg/auto-review/server/redis"
)

var baseTemplate = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .signin-container {
            padding: 40px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .logo {
            margin-bottom: 30px;
        }
        .btn-github {
            background-color: #24292e;
            color: white;
            padding: 12px 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .btn-github:hover {
            background-color: #3a3f46;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-12 col-md-8 col-lg-6">
			%s
            </div>
        </div>
    </div>
    <script>
    if(document.getElementById("team_token")) {
        document.getElementById("team_token").value = document.cookie.split("; ").find(row => row.startsWith("team_token=")).split("=")[1];
    }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/js/bootstrap.bundle.min.js"></script>
</body>
</html>`

var loginContent = `<div class="signin-container">
	<h2 class="mb-4">Welcome to AutoReview</h2>
	<p class="text-muted mb-4">Connect your GitHub account to get started</p>

	<a href="/auth">
	<button class="btn btn-github btn-lg w-100">
		<i class="fab fa-github me-2"></i> Sign in with GitHub
	</button>
	</a>
</div>`

var startInstanceContent, _ = template.New("startInstance").Parse(fmt.Sprintf(baseTemplate, "Instancer", `<div class="signin-container">
    <h2 class="mb-4">Welcome, {{.}}</h2>
    <form action="/newInstance" method="POST">
    <div class="mb-3 row align-items-center">
        <label for="team_token" class="form-label col-auto mb-0">Team Token:</label>
        <div class="col">
            <input type="text" class="form-control" name="team_token" id="team_token" placeholder="Enter team token" required>
        </div>
    </div>
    <button class="btn btn-github btn-lg w-100" type="submit">
        Create repository
    </button>
    </form>
</div>`))

var existingInstanceContent = `<div class="signin-container">
    <h2 class="mb-4">Your <a href="/repo">repo</a> has been created!</h2>
    <form action="/newInstance" method="POST">
        <div class="mb-3 row align-items-center">
           <label for="team_token" class="form-label col-auto mb-0">Team Token:</label>
            <div class="col">
                <input type="text" class="form-control" name="team_token" id="team_token" placeholder="Enter team token" required>
            </div>
        </div>
        <button class="btn btn-github btn-lg w-100" type="submit">
            Delete and re-create repository
        </button>
    </form>
    <p></p>
    <form action="/project" method="GET">
        <button class="btn btn-github btn-lg w-100" type="submit">
            View LLM token usage
        </button>
    </form>
</div>`

func HandleFrontPage(w http.ResponseWriter, req *http.Request) {
	u := getUserFromCookie(req)
	if u == nil {
		fmt.Fprintf(w, baseTemplate, "Sign in with GitHub", loginContent)
		return
	}
	exists, err := redis.ProjectExists(req.Context(), u.genProjectId())
	if err != nil {
		log.Default().Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if exists {
		fmt.Fprintf(w, baseTemplate, "Instancer", existingInstanceContent)
		return
	}
	startInstanceContent.Execute(w, u.Login)
}
