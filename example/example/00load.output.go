// from: skill.go
package src

type Skill struct {
	ID bson.ObjectId  bson:"_id" json:"id"
	Name SkillName  json:"name"
}

type SkillName string

// from: user.go
package src

import (
	strfmt "github.com/go-openapi/strfmt"
)

type User struct {
	Email Email  json:"email"
	FacebookAuthID *bson.ObjectId  bson:"facebookAuthId,omitempty" json:"facebookAuthId,omitempty"
	GithubAuthID *bson.ObjectId  bson:"githubAuthId,omitempty" json:"githubAuthId,omitempty"
	GoogleAuthID *bson.ObjectId  bson:"googleAuthId,omitempty" json:"googleAuthId,omitempty"
	ID bson.ObjectId  bson:"_id" json:"id"
	Name string  json:"name"
	TwitterAuthID *bson.ObjectId  bson:"twitterAuthId,omitempty" json:"twitterAuthId,omitempty"
}

type Email Email
