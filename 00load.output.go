package src

type Skill struct {
	Name SkillName  
}

type SkillName string
package src

import (
	strfmt "github.com/go-openapi/strfmt"
)

type User struct {
	Email Email  
	Name string  
}

type Email Email
