package api

import (
	"crypto/rand"
	"encoding/base64"
	"net/http"
	"strings"
	"time"

	"r3note/config"
	"r3note/middleware"
	"r3note/model"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func generateShareToken(n int) (string, error) {
	b := make([]byte, n)
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}
	return strings.TrimRight(base64.URLEncoding.EncodeToString(b), "="), nil
}

type ShareRequest struct {
	NoteID   string `json:"note_id" binding:"required"`
	ExpireIn int    `json:"expire_in" binding:"required"`
}

type ShareResponse struct {
	Token string `json:"token"`
}

type ShareNoteResponse struct {
	ID      string `json:"id"`
	Title   string `json:"title"`
	Content string `json:"content"`
	UserID  string `json:"user_id"`
}

func RegisterShareRoutes(r *gin.Engine, db *gorm.DB, cfg *config.Config) {
	share := r.Group("/api/share")
	share.Use(middleware.JWTAuthMiddleware())
	{
		share.POST("/create", func(c *gin.Context) { CreateShare(c, db, cfg) })
		share.GET("/list", func(c *gin.Context) { ListShares(c, db) })
		share.POST("/delete", func(c *gin.Context) { DeleteShare(c, db) })
	}
	shareNoAuth := r.Group("/api/share")
	{
		shareNoAuth.GET("/:id", func(c *gin.Context) { GetShare(c, db) })
	}
}

func CreateShare(c *gin.Context, db *gorm.DB, cfg *config.Config) {
	var req ShareRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.ExpireIn <= 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	userID := c.GetString("user_id")
	role := c.GetString("role")
	var note model.Note
	if err := db.Where("id = ?", req.NoteID).First(&note).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Note not found"})
		return
	}
	if note.UserID.String() != userID && role != "admin" {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Permission denied to share this note"})
		return
	}
	token, err := generateShareToken(16)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to generate share token"})
		return
	}
	share := model.Share{
		NoteID:   note.ID,
		UserID:   note.UserID,
		ExpireAt: time.Now().Add(time.Duration(req.ExpireIn) * time.Hour),
		Token:    token,
	}
	if err := db.Create(&share).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to create share link"})
		return
	}
	c.JSON(http.StatusOK, ShareResponse{Token: share.Token})
}

func GetShare(c *gin.Context, db *gorm.DB) {
	shareToken := c.Param("id")
	var share model.Share
	if err := db.Where("token = ?", shareToken).First(&share).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Share link not found"})
		return
	}
	if time.Now().After(share.ExpireAt) {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Share link expired"})
		return
	}
	var note model.Note
	if err := db.Where("id = ?", share.NoteID).First(&note).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Note not found"})
		return
	}
	resp := ShareNoteResponse{
		ID:      note.ID.String(),
		Title:   note.Title,
		Content: note.Content,
		UserID:  note.UserID.String(),
	}
	c.JSON(http.StatusOK, resp)
}

func ListShares(c *gin.Context, db *gorm.DB) {
	userID := c.GetString("user_id")
	var shares []model.Share
	if err := db.Where("user_id = ?", userID).Find(&shares).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to fetch shares"})
		return
	}
	var result []gin.H
	for _, s := range shares {
		var note model.Note
		db.Where("id = ?", s.NoteID).First(&note)
		result = append(result, gin.H{
			"id":        s.ID.String(),
			"noteTitle": note.Title,
			"expiry":    s.ExpireAt,
			"token":     s.Token,
		})
	}
	c.JSON(http.StatusOK, gin.H{"shares": result})
}

// DeleteShare removes a share link by id
func DeleteShare(c *gin.Context, db *gorm.DB) {
	var req struct {
		Id string `json:"id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	userID := c.GetString("user_id")
	var share model.Share
	if err := db.Where("id = ?", req.Id).First(&share).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Share not found"})
		return
	}
	if share.UserID.String() != userID {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Permission denied"})
		return
	}
	if err := db.Delete(&share).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to delete share"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true})
}
