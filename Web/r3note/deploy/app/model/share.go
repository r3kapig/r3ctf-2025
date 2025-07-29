package model

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type Share struct {
	ID       uuid.UUID `gorm:"type:char(36);primaryKey" json:"id"`
	NoteID   uuid.UUID `gorm:"type:char(36);index" json:"note_id"`
	UserID   uuid.UUID `gorm:"type:char(36);index" json:"user_id"`
	ExpireAt time.Time `json:"expire_at"`
	Token    string    `gorm:"size:32;uniqueIndex" json:"token"`
}

func (s *Share) BeforeCreate(tx *gorm.DB) (err error) {
	if s.ID == uuid.Nil {
		s.ID = uuid.New()
	}
	return
}
