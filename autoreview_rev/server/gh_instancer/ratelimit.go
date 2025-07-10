package gh_instancer

import (
	"fmt"
	"html/template"
	"net/http"
	"strings"

	"jro.sg/auto-review/server/redis"
)

const rateLimitHtmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Rate limits</title>
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
        <h1>Admin Dashboard - Rate limits</h1>

        {{if .}}
        <table>
            <thead>
                <tr>
                    <th>Key</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {{range .}}
                <tr>
                    <td><span class="key-name">{{.}}</span></td>
					<td><span class="value-cell">
                        <form method="POST" action="/admin/reset"><input name="key_id" type=hidden value="limiter_{{.}}"><button type="submit">Delete</button></form>
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

func HandleRateLimitStats(w http.ResponseWriter, r *http.Request) {
	client := redis.GetClient()
	ctx := r.Context()

	var keys []string

	iter := client.Scan(ctx, 0, "limiter_*", 0).Iterator()

	for iter.Next(ctx) {
		keys = append(keys, strings.Split(iter.Val(), "limiter_")[1])
	}
	if err := iter.Err(); err != nil {
		http.Error(w, fmt.Sprintf("error scanning keys: %v", err.Error()), http.StatusInternalServerError)
		return
	}

	tmpl, err := template.New("rl_keys").Parse(rateLimitHtmlTemplate)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error parsing template: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := tmpl.Execute(w, keys); err != nil {
		http.Error(w, fmt.Sprintf("Error executing template: %v", err), http.StatusInternalServerError)
		return
	}
}
