package api

import (
	"net/http"

	"r3note/config"
	"r3note/middleware"
	"r3note/model"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

type NoteRequest struct {
	ID      string `json:"id"` // For edit/delete
	Title   string `json:"title"`
	Content string `json:"content"`
}

type NoteSearchRequest struct {
	Keyword string `form:"keyword"`
}

type NoteResponse struct {
	ID      string `json:"id"`
	Title   string `json:"title"`
	Content string `json:"content"`
	UserID  string `json:"user_id"`
}

func GetNote(c *gin.Context, db *gorm.DB) {
	noteID := c.Param("id")
	userID := c.GetString("user_id")
	role := c.GetString("role")
	var note model.Note
	if err := db.Where("id = ?", noteID).First(&note).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Note not found"})
		return
	}
	if note.UserID.String() != userID && role != "admin" {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Permission denied"})
		return
	}
	resp := NoteResponse{
		ID:      note.ID.String(),
		Title:   note.Title,
		Content: note.Content,
		UserID:  note.UserID.String(),
	}
	c.JSON(http.StatusOK, resp)
}

func RegisterNoteRoutes(r *gin.Engine, db *gorm.DB, cfg *config.Config) {
	note := r.Group("/api/note")
	note.Use(middleware.JWTAuthMiddleware())
	{
		note.POST("/create", func(c *gin.Context) { CreateNote(c, db) })
		note.POST("/delete", func(c *gin.Context) { DeleteNote(c, db) })
		note.POST("/edit", func(c *gin.Context) { EditNote(c, db) })
		note.GET("/list", func(c *gin.Context) { ListNotes(c, db) })
		note.GET("/:id", func(c *gin.Context) { GetNote(c, db) })
	}
}

func CreateNote(c *gin.Context, db *gorm.DB) {
	var req NoteRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	userID := c.GetString("user_id")
	note := model.Note{
		Title:   req.Title,
		Content: req.Content,
		UserID:  uuid.MustParse(userID),
	}
	if err := db.Create(&note).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to create note"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"msg": "Note created", "id": note.ID})
}

func DeleteNote(c *gin.Context, db *gorm.DB) {
	var req NoteRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.ID == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	userID := c.GetString("user_id")
	role := c.GetString("role")
	var note model.Note
	if err := db.Where("id = ?", req.ID).First(&note).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Note not found"})
		return
	}
	if note.UserID.String() != userID && role != "admin" {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Permission denied"})
		return
	}
	if err := db.Delete(&note).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to delete note"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"msg": "Note deleted"})
}

func EditNote(c *gin.Context, db *gorm.DB) {
	var req NoteRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.ID == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	userID := c.GetString("user_id")
	role := c.GetString("role")
	var note model.Note
	if err := db.Where("id = ?", req.ID).First(&note).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Note not found"})
		return
	}
	if note.UserID.String() != userID && role != "admin" {
		c.JSON(http.StatusForbidden, ErrorResponse{Error: "Permission denied"})
		return
	}
	note.Title = req.Title
	note.Content = req.Content
	if err := db.Save(&note).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to update note"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"msg": "Note updated"})
}

func ListNotes(c *gin.Context, db *gorm.DB) {
	userID := c.GetString("user_id")
	role := c.GetString("role")
	var notes []model.Note
	query := db
	if role != "admin" {
		query = query.Where("user_id = ?", userID)
	}
	if err := query.Find(&notes).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to list notes"})
		return
	}
	var resp []NoteResponse
	for _, n := range notes {
		resp = append(resp, NoteResponse{
			ID:      n.ID.String(),
			Title:   n.Title,
			Content: n.Content,
			UserID:  n.UserID.String(),
		})
	}
	c.JSON(http.StatusOK, resp)
}
