package main

import (
	"r3note/api"
	"r3note/config"
	"r3note/middleware"
	"r3note/model"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.InitConfig()
	db := model.InitDB(cfg.Database.Path)
	model.AutoMigrate(db)
	r := gin.Default()
	r.Use(middleware.SecureMiddleware())
	api.RegisterRoutes(r, db, cfg)
	r.Run(cfg.Server.Port)
}
