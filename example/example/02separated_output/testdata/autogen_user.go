package testdata

import (
	src "github.com/podhmo/hmm/src"
	bson "gopkg.in/mgo.v2/bson"
)

// EmptyUser : creates empty User
func EmptyUser() src.User {
	value := src.User {
		ID: bson.NewObjectId(),
	}
	return value
}

// User : creates User with modify function
func User(modify func(value *src.User)) *src.User {
	value := EmptyUser()
	modify(&value)
	return &value
}