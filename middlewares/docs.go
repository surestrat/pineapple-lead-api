package middlewares

import (
	"net/http"
	"path/filepath"
	"strings"
)

// ServeSwaggerUI serves the Swagger UI frontend
func ServeSwaggerUI(staticDir string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Strip the /swagger/ prefix from the URL path
		path := strings.TrimPrefix(r.URL.Path, "/swagger/")
		
		// If no specific file is requested, serve index.html
		if path == "" || path == "/" {
			path = "index.html"
		}
		
		// Serve the requested file from the static directory
		http.ServeFile(w, r, filepath.Join(staticDir, path))
	}
}

// RedirectToDocs redirects to the Swagger UI
func RedirectToDocs(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "/swagger/", http.StatusFound)
}
