package src

import "gopkg.in/mgo.v2/bson"

type SkillName string

type Skill struct {
	ID   bson.ObjectId `bson:"_id" json:"id"`
	Name SkillName     `json:"name"`
}
