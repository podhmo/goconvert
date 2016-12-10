package dst

import "github.com/go-openapi/strfmt"

// Email :
type Email strfmt.Email

// ID :
type ID string

// Father :
type Father *User

// Age :
type Age int64

// User :
type User struct {
	ID             *ID
	Age            Age
	Name           *string
	Father         Father
	Mother         *User
	Email          *Email
	Address        *Address
	GoogleAuthID   *ID
	TwitterAuthID  *ID
	FacebookAuthID *ID
	GithubAuthID   *ID
	Skills         []Skill
	Skills2        []Skill
	Skills3        *[]Skill
	Skills4        []Skill
	Skills5        []*Skill
	Skills6        SkillSet
	Skills7        []*Skill
}

// SkillSet :
type SkillSet []Skill

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
