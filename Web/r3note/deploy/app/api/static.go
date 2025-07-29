package api

import (
	"r3note/config"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func RegisterStaticRoutes(r *gin.Engine, db *gorm.DB, cfg *config.Config) {
	r.Static("/files", cfg.Static.Path)

	r.NoRoute(func(c *gin.Context) {
		c.File(cfg.Static.Index)
	})
}
