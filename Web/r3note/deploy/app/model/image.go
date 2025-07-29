package model

import (
	"github.com/google/uuid"
	"gorm.io/gorm"
)

type Image struct {
	ID         uuid.UUID `gorm:"type:char(36);primaryKey" json:"id"`
	UserID     uuid.UUID `gorm:"type:char(36);index" json:"user_id"`
	FileName   string    `gorm:"not null" json:"file_name"`
	OriginName string    `gorm:"not null" json:"origin_name"`
}

func (img *Image) BeforeCreate(tx *gorm.DB) (err error) {
	if img.ID == uuid.Nil {
		img.ID = uuid.New()
	}
	return
}
