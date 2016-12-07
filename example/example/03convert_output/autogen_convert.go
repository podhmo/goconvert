package convert

import (
	dst "github.com/podhmo/hmm/dst"
	src "github.com/podhmo/hmm/src"
)

func UserToUser(src *src.User) *dst.User {
	dst := &dst.User{}
	dst.Address = AddressToAddress(src.Address)
	tmp1 := dst.Email(src.Email)
	dst.Email = &(tmp1)
	dst.FacebookAuthID = ConvertIDPtr(src.FacebookAuthID)
	dst.GithubAuthID = ConvertIDPtr(src.GithubAuthID)
	dst.GoogleAuthID = ConvertIDPtr(src.GoogleAuthID)
	dst.ID = ConvertID(src.Id)
	dst.Name = &(src.Name)
	dst.TwitterAuthID = ConvertIDPtr(src.TwitterAuthID)
	// FIXME: missing FullName
	return dst
}

func AddressToAddress(src *src.Address) *dst.Address {
	dst := &dst.Address{}
	dst.Address = &(src.Address)
	return dst
}
