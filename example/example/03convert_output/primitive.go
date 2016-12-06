package convert

import (
	"github.com/podhmo/hmm/def"
	"github.com/wacul/ptr"
)

// ConvertID will convert bson.ObjectId to *def.ID
func ConvertID(id interface {
	Hex() string
}) *def.ID {
	if id == nil {
		return nil
	}
	return (*def.ID)(ptr.String(id.Hex()))
}
