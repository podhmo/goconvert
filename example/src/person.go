package src

import "github.com/go-openapi/strfmt"

// Email :
type Email strfmt.Email

// User :
type User struct {
	Name  string `json:"name"`
	Email Email  `json:"email"`
}