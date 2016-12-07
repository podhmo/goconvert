package dst

import "github.com/go-openapi/strfmt"

// Email :
type Email strfmt.Email

// ID :
type ID string

// User :
type User struct {
	ID             *ID
	Name           *string
	FullName       *string
	Email          *Email
	Address        *Address
	GoogleAuthID   *ID
	TwitterAuthID  *ID
	FacebookAuthID *ID
	GithubAuthID   *ID
}

// Address :
type Address struct {
	Address *string
}
