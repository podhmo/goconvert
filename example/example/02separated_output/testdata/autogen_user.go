package testdata

import (
	src "github.com/podhmo/hmm/src"
	bson "gopkg.in/mgo.v2/bson"
)

// EmptyAddress : returns empty Address
func EmptyAddress() src.Address {
	value := src.Address{}
	return value
}

// Address : creates Address with modify function
func Address(modify func(value *src.Address)) *src.Address {
	value := EmptyAddress()
	modify(&value)
	return &value
}

// EmptyUser : returns empty User
func EmptyUser() src.User {
	value := src.User{
		Id: bson.NewObjectId(),
	}
	return value
}

// User : creates User with modify function
func User(modify func(value *src.User)) *src.User {
	value := EmptyUser()
	modify(&value)
	return &value
}
