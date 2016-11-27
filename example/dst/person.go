package dst

import "github.com/go-openapi/strfmt"

// Email :
type Email strfmt.Email

// ID :
type ID string

// User :
type User struct {
	ID    *ID
	Name  *string
	Email *Email
}
