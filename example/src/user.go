package src

import (
	"github.com/go-openapi/strfmt"
	"gopkg.in/mgo.v2/bson"
)

// Email :
type Email strfmt.Email

// User :
type User struct {
	Id             bson.ObjectId  `bson:"_id" json:"id"`
	Name           string         `json:"name"`
	LastName       string         `json:"lastname"`
	Email          Email          `json:"email"`
	GoogleAuthID   *bson.ObjectId `bson:"googleAuthId,omitempty" json:"googleAuthId,omitempty"`
	TwitterAuthID  *bson.ObjectId `bson:"twitterAuthId,omitempty" json:"twitterAuthId,omitempty"`
	FacebookAuthID *bson.ObjectId `bson:"facebookAuthId,omitempty" json:"facebookAuthId,omitempty"`
	GithubAuthID   *bson.ObjectId `bson:"githubAuthId,omitempty" json:"githubAuthId,omitempty"`
	Address        *Address       `json:"address"`
}

// FullUser
type FullUser struct {
	User
	FullName string `json:"fullname"`
}

// Address :
type Address struct {
	Address string
}
