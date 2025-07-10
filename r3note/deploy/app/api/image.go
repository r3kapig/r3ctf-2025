package api

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"

	"r3note/config"
	"r3note/middleware"
	"r3note/model"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

func RegisterImageRoutes(r *gin.Engine, db *gorm.DB, cfg *config.Config) {
	img := r.Group("/api/image")
	img.Use(middleware.JWTAuthMiddleware())
	{
		img.POST("/upload", func(c *gin.Context) { UploadImage(c, db, cfg) })
	}

	imgNoAuth := r.Group("/api/image")
	{
		imgNoAuth.GET("/:id", func(c *gin.Context) { GetImage(c, db, cfg) })
	}
}

func UploadImage(c *gin.Context, db *gorm.DB, cfg *config.Config) {
	userID := c.GetString("user_id")
	file, header, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "No file selected"})
		return
	}
	defer file.Close()
	imgID := uuid.New()
	ext := filepath.Ext(header.Filename)
	if ext == "" || ext == ".js" || ext == ".css" || ext == ".html" {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid file type"})
		return
	}
	fileName := imgID.String() + ext
	userDir := filepath.Join(cfg.Upload.Path, userID)
	if err := os.MkdirAll(userDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to create user directory"})
		return
	}
	filePath := filepath.Join(userDir, fileName)
	out, err := os.Create(filePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to save file"})
		return
	}
	defer out.Close()
	if _, err := io.Copy(out, file); err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to write file"})
		return
	}
	img := model.Image{
		ID:         imgID,
		UserID:     uuid.MustParse(userID),
		FileName:   fileName,
		OriginName: header.Filename,
	}
	if err := db.Create(&img).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to save image to database"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"msg": "Upload successful", "id": imgID.String()})
}

func GetImage(c *gin.Context, db *gorm.DB, cfg *config.Config) {
	imgID := c.Param("id")
	var img model.Image
	if err := db.Where("id = ?", imgID).First(&img).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Image not found"})
		return
	}

	ref := c.Request.Referer()

	if ref == "" {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Forbidden"})
		return
	}

	refURL, err := url.Parse(ref)
	if err != nil {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Forbidden"})
	}

	fmt.Println(refURL.Host, c.Request.Host)
	if refURL.Host != c.Request.Host {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Forbidden"})
		return
	}

	filePath := filepath.Join(cfg.Upload.Path, img.UserID.String(), img.FileName)
	if _, err := os.Stat(filePath); err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "File not found"})
		return
	}
	c.File(filePath)
}
