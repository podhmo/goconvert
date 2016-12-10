// from: skill.go
package src

import (
	bson "gopkg.in/mgo.v2/bson"
)

type Skill struct {
	ID bson.ObjectId  `bson:"_id" json:"id"`
	Name SkillName  `json:"name"`
}

type SkillName string

// from: user.go
package src

import (
	bson "gopkg.in/mgo.v2/bson"
	strfmt "github.com/go-openapi/strfmt"
	src "github.com/podhmo/hmm/src"
)

type Address struct {
	Address string
}

type FullUser struct {
	FullName string  `json:"fullname"`
	User
}

type User struct {
	Address *Address  `bson:"addresss" json:"address"`
	Age int  `json:"age"`
	Email Email  `json:"email"`
	FacebookAuthID *bson.ObjectId  `bson:"facebookAuthId,omitempty" json:"facebookAuthId,omitempty"`
	Father *User  `bson:"-" json:"father"`
	GithubAuthID *bson.ObjectId  `bson:"githubAuthId,omitempty" json:"githubAuthId,omitempty"`
	GoogleAuthID *bson.ObjectId  `bson:"googleAuthId,omitempty" json:"googleAuthId,omitempty"`
	Id bson.ObjectId  `bson:"_id" json:"id"`
	LastName string  `json:"lastname"`
	Mother Mother  `bson:"-" json:"mother"`
	Name string  `json:"name"`
	Skills []Skill  `bson:"skills" json:"skills"`
	Skills2 *[]Skill  `bson:"skills2" json:"skills2"`
	Skills3 []Skill  `bson:"skills3" json:"skills3"`
	Skills4 []*Skill  `bson:"skills4" json:"skills4"`
	Skills5 []Skill  `bson:"skills5" json:"skills5"`
	Skills6 []Skill  `bson:"skills6" json:"skills6"`
	Skills7 SkillSet  `bson:"skills7" json:"skills7"`
	TwitterAuthID *bson.ObjectId  `bson:"twitterAuthId,omitempty" json:"twitterAuthId,omitempty"`
}

type Email Email

type Mother *User

type S Skill

type SkillSet []Skill
