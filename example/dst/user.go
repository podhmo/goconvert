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
	Email          *Email
	Address        *Address
	GoogleAuthID   *ID
	TwitterAuthID  *ID
	FacebookAuthID *ID
	GithubAuthID   *ID
	Skills         []Skill
}

// FullUser :
type FullUser struct {
	FullName *string
	*User
}

// Address :
type Address struct {
	Address *string
}

// Skill :
type Skill struct {
	ID   *ID
	Name *string
}
