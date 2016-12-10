package convert

import (
	"github.com/podhmo/hmm/dst"
	"gopkg.in/mgo.v2/bson"
)

// ConvertID will convert bson.ObjectId to *dst.ID
func ConvertID(id bson.ObjectId) *dst.ID {
	x := id.Hex()
	return (*dst.ID)(&x)
}

// ConvertIDPtr will convert bson.ObjectId to *dst.ID
func ConvertIDPtr(id *bson.ObjectId) *dst.ID {
	if id == nil {
		return nil
	}
	x := id.Hex()
	return (*dst.ID)(&x)
}
