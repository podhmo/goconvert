// from: skill.go
package src

type Skill struct {
	Name SkillName  json:"name"
}

type SkillName string

// from: person.go
package src

import (
	strfmt "github.com/go-openapi/strfmt"
)

type User struct {
	Email Email  json:"email"
	Name string  json:"name"
}

type Email Email
