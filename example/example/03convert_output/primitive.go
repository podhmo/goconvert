package convert

import (
	"github.com/podhmo/hmm/dst"
	"gopkg.in/mgo.v2/bson"
)

// ConvertID will convert bson.ObjectId to *dst.ID
func ConvertID(id bson.ObjectId) *dst.ID {
	if id == nil {
		return nil
	}
    x := id.Hex()
	return (*dst.ID)(&x)
}
