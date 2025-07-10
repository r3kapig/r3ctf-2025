package config

import (
	"github.com/spf13/viper"
)

type Config struct {
	Server struct {
		Port string
	}
	JWT struct {
		Secret string
	}
	Database struct {
		Path string
	}
	Upload struct {
		Path string
	}
	Static struct {
		Path  string
		Index string
	}
}

func InitConfig() *Config {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	if err := viper.ReadInConfig(); err != nil {
		panic(err)
	}
	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		panic(err)
	}
	return &cfg
}
