package model

import (
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func InitDB(path string) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(path), &gorm.Config{})
	if err != nil {
		panic("failed to connect database: " + err.Error())
	}
	return db
}

func AutoMigrate(db *gorm.DB) {
	db.AutoMigrate(&User{}, &Note{}, &Image{}, &Share{})
}
