package testdata

import (
	src "github.com/podhmo/hmm/src"
	bson "gopkg.in/mgo.v2/bson"
)

// EmptySkill : creates empty Skill
func EmptySkill() src.Skill {
	value := src.Skill {
		ID: bson.NewObjectId(),
	}
	return value
}

// Skill : creates Skill with modify function
func Skill(modify func(value *src.Skill)) *src.Skill {
	value := EmptySkill()
	modify(&value)
	return &value
}