package api

import (
	"r3note/config"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type ErrorResponse struct {
	Error string `json:"error"`
}

func RegisterRoutes(r *gin.Engine, db *gorm.DB, cfg *config.Config) {
	RegisterUserRoutes(r, db, cfg)
	RegisterNoteRoutes(r, db, cfg)
	RegisterImageRoutes(r, db, cfg)
	RegisterShareRoutes(r, db, cfg)
	RegisterStaticRoutes(r, db, cfg)
}
