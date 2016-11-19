package src

import (
	"time"

	"gopkg.in/mgo.v2/bson"
)

type AuthStatus string

// AuthStatus :
const (
	AuthStatusInvalid = AuthStatus("invalid")
	AuthStatusValid   = AuthStatus("valid")
)

type GoogleAuth struct {
	Id          bson.ObjectId `bson:"_id"`
	UserId      bson.ObjectId `bson:"userId"`
	Name        string        `bson:"name"`
	AccessToken string        `bson:"accessToken"`
	Expiry      time.Time     `bson:"expiry"`
	Status      AuthStatus    `bson:"status"`
}

type FacebookAuth struct {
	Id          bson.ObjectId `bson:"_id"`
	UserId      bson.ObjectId `bson:"userId"`
	AccountId   string        `bson:"accountId"`
	Name        string        `bson:"name"`
	AccessToken string        `bson:"accessToken"`
	Expiry      time.Time     `bson:"expiry"`
	Status      AuthStatus    `bson:"status"`
}

type TwitterAuth struct {
	Id          bson.ObjectId `bson:"_id"`
	UserId      bson.ObjectId `bson:"userId"`
	Name        string        `bson:"name"`
	AccessToken string        `bson:"accessToken"`
	Expiry      time.Time     `bson:"expiry"`
	Status      AuthStatus    `bson:"status"`
}

type GithubAuth struct {
	Id          bson.ObjectId `bson:"_id"`
	UserId      bson.ObjectId `bson:"userId"`
	Name        string        `bson:"name"`
	AccessToken string        `bson:"accessToken"`
	Expiry      time.Time     `bson:"expiry"`
	Status      AuthStatus    `bson:"status"`
}
