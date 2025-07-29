package gh_instancer

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
)

func (u *user) genFlag(teamToken string) (string, error) {
	flag := os.Getenv("FLAG")

	if len(flag) < 33 {
		panic("$FLAG must be at least 33 characters long")
	}

	secretKey := os.Getenv("SECRET_KEY")

	if len(secretKey) < 32 {
		panic("$SECRET_KEY must be at least 32 characters long!")
	}

	h := hmac.New(sha256.New, []byte(secretKey))
	h.Write([]byte(teamToken))
	key := h.Sum(nil)

	ecb, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(ecb)
	if err != nil {
		return "", err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return "", err
	}

	ct := hex.EncodeToString(gcm.Seal(nonce, nonce, []byte(u.Login), nil))
	return fmt.Sprintf("%s_%s}", flag[:len(flag)-1], ct), nil
}
