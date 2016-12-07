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
)

type Address struct {
	Address string
}

type User struct {
	Address *Address  `json:"address"`
	Email Email  `json:"email"`
	FacebookAuthID *bson.ObjectId  `bson:"facebookAuthId,omitempty" json:"facebookAuthId,omitempty"`
	GithubAuthID *bson.ObjectId  `bson:"githubAuthId,omitempty" json:"githubAuthId,omitempty"`
	GoogleAuthID *bson.ObjectId  `bson:"googleAuthId,omitempty" json:"googleAuthId,omitempty"`
	Id bson.ObjectId  `bson:"_id" json:"id"`
	LastName string  `json:"lastname"`
	Name string  `json:"name"`
	TwitterAuthID *bson.ObjectId  `bson:"twitterAuthId,omitempty" json:"twitterAuthId,omitempty"`
}

type Email Email
