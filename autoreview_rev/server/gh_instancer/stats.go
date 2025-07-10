package gh_instancer

import (
	"fmt"
	"html/template"
	"net/http"
	"os"
	"strings"

	"jro.sg/auto-review/server/redis"
)

const htmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .info {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #2196f3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .key-name {
            font-family: monospace;
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 2px;
        }
        .value-cell {
            max-width: 300px;
            word-wrap: break-word;
            font-family: monospace;
            font-size: 0.9em;
        }
        .refresh-btn {
            background-color: #4caf50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Dashboard</h1>

		GH Token 1: {{.Token1Usage}} <br>
		GH Token 2: {{.Token2Usage}}

        {{if .Stats}}
        <table>
            <thead>
                <tr>
                    <th>Project ID</th>
                    <th>Owner</th>
                    <th>Tokens Used</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {{range .Stats}}
                <tr>
                    <td><span class="key-name">{{.ProjectId}}</span></td>
					<td><span class="value-cell"><a href="{{.RepoUrl}}" target="_blank">{{.Owner}}</a></span></td>
					<td><span class="value-cell">{{.TokensUsed}}</span></td>
					<td><span class="value-cell">
                        <form method="POST" action="/admin/projects/{{.ProjectId}}/usage/reset"><button type="submit">Reset token usage</button></form>
                        <form method="POST" action="/admin/reset"><input type=hidden value="created_project:{{.Owner}}"><button type="submit">Reset rate limit</button></form>
                    </td>
                </tr>
                {{end}}
            </tbody>
        </table>
        {{else}}
        <p style="text-align: center; color: #666; font-style: italic;">No keys found in the database.</p>
        {{end}}
    </div>
</body>
</html>
`

type projectStats struct {
	ProjectId  string
	Owner      string
	TokensUsed int
	RepoUrl    string
}

type pageData struct {
	Stats       []*projectStats
	Token1Usage string
	Token2Usage string
}

func HandleStats(w http.ResponseWriter, r *http.Request) {
	client := redis.GetClient()
	ctx := r.Context()
	orgName := os.Getenv("ORG_NAME")

	var projectIds []string

	iter := client.Scan(ctx, 0, "project_owner:*", 0).Iterator()

	for iter.Next(ctx) {
		projectIds = append(projectIds, strings.Split(iter.Val(), ":")[1])
	}
	if err := iter.Err(); err != nil {
		http.Error(w, fmt.Sprintf("error scanning keys: %v", err.Error()), http.StatusInternalServerError)
		return
	}

	projects := make([]*projectStats, len(projectIds))
	for i, id := range projectIds {
		owner, err := redis.GetProjectOwner(ctx, id)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		tokensUsed, err := redis.GetProjectTokenUsage(ctx, id)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		targetRepoName := "revenge-auto-review-" + owner
		repoUrl := fmt.Sprintf("https://github.com/%s/%s", orgName, targetRepoName)
		projects[i] = &projectStats{
			ProjectId:  id,
			Owner:      owner,
			TokensUsed: tokensUsed,
			RepoUrl:    repoUrl,
		}
	}

	token1Usage := getUsageMessage(r.Context(), getClient(1))
	token2Usage := getUsageMessage(r.Context(), getClient(2))

	tmpl, err := template.New("keys").Parse(htmlTemplate)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error parsing template: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := tmpl.Execute(w, pageData{
		Stats:       projects,
		Token1Usage: token1Usage,
		Token2Usage: token2Usage,
	}); err != nil {
		http.Error(w, fmt.Sprintf("Error executing template: %v", err), http.StatusInternalServerError)
		return
	}
}

func HandleReset(w http.ResponseWriter, r *http.Request) {
	keyId := r.FormValue("key_id")
	if keyId == "" {
		http.Error(w, "missing key_id in form", http.StatusBadRequest)
		return
	}
	ctx := r.Context()
	err := redis.DeleteKey(ctx, keyId)
	if err != nil {
		http.Error(w, fmt.Sprintf("error deleting key: %v", err.Error()), http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "Key %s deleted successfully", keyId)
}
