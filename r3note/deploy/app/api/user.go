package api

import (
	"net/http"
	"time"

	"r3note/config"
	"r3note/middleware"
	"r3note/model"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type RegisterRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	Username string `json:"username"`
	Role     string `json:"role"`
	Token    string `json:"token"`
}

type UserInfoResponse struct {
	ID       string `json:"id"`
	Username string `json:"username"`
	Role     string `json:"role"`
}

func Register(c *gin.Context, db *gorm.DB) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	var user model.User
	if err := db.Where("username = ?", req.Username).First(&user).Error; err == nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Username already exists"})
		return
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Password encryption failed"})
		return
	}
	user = model.User{
		Username: req.Username,
		Password: string(hash),
		Role:     "user",
	}
	if err := db.Create(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Registration failed"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"msg": "Registration successful"})
}

func Login(c *gin.Context, db *gorm.DB, cfg *config.Config) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid parameters"})
		return
	}
	var user model.User
	if err := db.Where("username = ?", req.Username).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "Invalid username or password"})
		return
	}
	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "Invalid username or password"})
		return
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"id":   user.ID.String(),
		"role": user.Role,
		"exp":  time.Now().Add(24 * time.Hour).Unix(),
	})
	tokenString, err := token.SignedString([]byte(cfg.JWT.Secret))
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Failed to generate token"})
		return
	}
	c.JSON(http.StatusOK, LoginResponse{
		Username: user.Username,
		Role:     user.Role,
		Token:    tokenString,
	})
}

func GetMe(c *gin.Context, db *gorm.DB) {
	userID := c.GetString("user_id")
	var user model.User
	if err := db.Where("id = ?", userID).First(&user).Error; err != nil {
		c.JSON(401, ErrorResponse{Error: "User not found"})
		return
	}
	resp := UserInfoResponse{
		ID:       user.ID.String(),
		Username: user.Username,
		Role:     user.Role,
	}
	c.JSON(200, resp)
}

func RegisterUserRoutes(r *gin.Engine, db *gorm.DB, cfg *config.Config) {
	user := r.Group("/api/user")
	{
		user.POST("/register", func(c *gin.Context) { Register(c, db) })
		user.POST("/login", func(c *gin.Context) { Login(c, db, cfg) })
	}
	userAuth := r.Group("/api/user")
	userAuth.Use(middleware.JWTAuthMiddleware())
	{
		userAuth.GET("/me", func(c *gin.Context) { GetMe(c, db) })
	}
}
