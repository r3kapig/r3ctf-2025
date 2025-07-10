package model

import (
	"github.com/google/uuid"
	"gorm.io/gorm"
)

type Note struct {
	ID      uuid.UUID `gorm:"type:char(36);primaryKey" json:"id"`
	Title   string    `gorm:"not null" json:"title"`
	Content string    `gorm:"type:text" json:"content"`
	UserID  uuid.UUID `gorm:"type:char(36);index" json:"user_id"`
}

func (n *Note) BeforeCreate(tx *gorm.DB) (err error) {
	if n.ID == uuid.Nil {
		n.ID = uuid.New()
	}
	return
}
