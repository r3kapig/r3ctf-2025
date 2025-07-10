package model

import (
	"github.com/google/uuid"
	"gorm.io/gorm"
)

type User struct {
	ID       uuid.UUID `gorm:"type:char(36);primaryKey" json:"id"`
	Username string    `gorm:"uniqueIndex;not null" json:"username"`
	Password string    `gorm:"not null" json:"-"`
	Role     string    `gorm:"not null" json:"role"` // user or admin
}

func (u *User) BeforeCreate(tx *gorm.DB) (err error) {
	if u.ID == uuid.Nil {
		u.ID = uuid.New()
	}
	return
}
