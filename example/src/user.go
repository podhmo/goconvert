package src

import (
	"github.com/go-openapi/strfmt"
	"gopkg.in/mgo.v2/bson"
)

// Email :
type Email strfmt.Email

// Mother :
type Mother *User

// User :
type User struct {
	Id             bson.ObjectId  `bson:"_id" json:"id"`
	Name           string         `json:"name"`
	Age            int            `json:"age"`
	Father         *User          `json:"father" bson:"-"`
	Mother         Mother         `json:"mother" bson:"-"`
	LastName       string         `json:"lastname"`
	Email          Email          `json:"email"`
	GoogleAuthID   *bson.ObjectId `bson:"googleAuthId,omitempty" json:"googleAuthId,omitempty"`
	TwitterAuthID  *bson.ObjectId `bson:"twitterAuthId,omitempty" json:"twitterAuthId,omitempty"`
	FacebookAuthID *bson.ObjectId `bson:"facebookAuthId,omitempty" json:"facebookAuthId,omitempty"`
	GithubAuthID   *bson.ObjectId `bson:"githubAuthId,omitempty" json:"githubAuthId,omitempty"`
	Address        *Address       `bson:"addresss" json:"address"`
	Skills         []Skill        `bson:"skills" json:"skills"`
	Skills2        *[]Skill       `bson:"skills2" json:"skills2"`
	Skills3        []Skill        `bson:"skills3" json:"skills3"`
	Skills4        []*Skill       `bson:"skills4" json:"skills4"`
	Skills5        []Skill        `bson:"skills5" json:"skills5"`
	Skills6        []Skill        `bson:"skills6" json:"skills6"`
	Skills7        SkillSet       `bson:"skills7" json:"skills7"`
}

// SkillSet :
type SkillSet []Skill

// S :
type S Skill

// FullUser
type FullUser struct {
	User
	FullName string `json:"fullname"`
}

// Address :
type Address struct {
	Address string
}
