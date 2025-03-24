// middlewares/rate_limit.go
package middlewares

import (
	"net/http"
	"time"

	"github.com/didip/tollbooth/v7"
	"github.com/didip/tollbooth/v7/limiter"
	"github.com/didip/tollbooth_chi"
)

var tbLimiter *limiter.Limiter

func init() {
    // Configure the rate limiter: 10 requests per second with a 1 second TTL
    tbLimiter = tollbooth.NewLimiter(10, &limiter.ExpirableOptions{DefaultExpirationTTL: time.Second})
    
    // Set a message for rejected requests
    tbLimiter.SetMessage(`{"success":false,"error":"Too many requests. Please try again later."}`)
    
    // Set up custom headers
    tbLimiter.SetMessageContentType("application/json")
    
    // Configure to use IP address as the limiter key
    tbLimiter.SetIPLookups([]string{"X-Forwarded-For", "X-Real-IP", "RemoteAddr"})
}

// RateLimitMiddleware limits the number of requests per time period
func RateLimitMiddleware(next http.Handler) http.Handler {
    handler := tollbooth_chi.LimitHandler(tbLimiter)
    return handler(next)
}