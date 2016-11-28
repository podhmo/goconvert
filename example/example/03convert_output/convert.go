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
	if src.FacebookAuthID != nil {
		tmp2 := *(src.FacebookAuthID)
		tmp3 := dst.ID(tmp2)
		dst.FacebookAuthID = &(tmp3)
	}
	if src.GithubAuthID != nil {
		tmp4 := *(src.GithubAuthID)
		tmp5 := dst.ID(tmp4)
		dst.GithubAuthID = &(tmp5)
	}
	if src.GoogleAuthID != nil {
		tmp6 := *(src.GoogleAuthID)
		tmp7 := dst.ID(tmp6)
		dst.GoogleAuthID = &(tmp7)
	}
	tmp8 := dst.ID(src.Id)
	dst.ID = &(tmp8)
	dst.Name = &(src.Name)
	if src.TwitterAuthID != nil {
		tmp9 := *(src.TwitterAuthID)
		tmp10 := dst.ID(tmp9)
		dst.TwitterAuthID = &(tmp10)
	}
	return dst
}

func AddressToAddress(src *src.Address) *dst.Address {
	dst := &dst.Address{}
	dst.Address = &(src.Address)
	return dst
}
