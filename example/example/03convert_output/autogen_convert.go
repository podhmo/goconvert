package convert

import (
	dst "github.com/podhmo/hmm/dst"
	src "github.com/podhmo/hmm/src"
)

// UserToUser :
func UserToUser(from *src.User) *dst.User {
	to := &dst.User{}
	to.Address = AddressToAddress(from.Address)
	tmp1 := (dst.Age)(from.Age)
	to.Age = tmp1
	tmp2 := (dst.Email)(from.Email)
	to.Email = &(tmp2)
	if from.FacebookAuthID != nil {
		tmp3 := *(from.FacebookAuthID)
		tmp4 := (dst.ID)(tmp3)
		to.FacebookAuthID = &(tmp4)
	}
	tmp5 := UserToUser(from.Father)
	tmp6 := (dst.Father)(tmp5)
	to.Father = tmp6
	if from.GithubAuthID != nil {
		tmp7 := *(from.GithubAuthID)
		tmp8 := (dst.ID)(tmp7)
		to.GithubAuthID = &(tmp8)
	}
	if from.GoogleAuthID != nil {
		tmp9 := *(from.GoogleAuthID)
		tmp10 := (dst.ID)(tmp9)
		to.GoogleAuthID = &(tmp10)
	}
	tmp11 := (dst.ID)(from.Id)
	to.ID = &(tmp11)
	tmp12 := (*src.User)(from.Mother)
	to.Mother = UserToUser(tmp12)
	to.Name = &(from.Name)
	to.Skills = SkillManyToSkillMany(from.Skills)
	tmp13 := SkillManyToSkillMany(from.Skills6)
	tmp14 := (dst.SkillSet)(tmp13)
	to.Skills6 = tmp14
	tmp15 := ([]src.Skill)(from.Skills7)
	to.Skills7 = SkillManyToSkillRefMany(tmp15)
	if from.TwitterAuthID != nil {
		tmp16 := *(from.TwitterAuthID)
		tmp17 := (dst.ID)(tmp16)
		to.TwitterAuthID = &(tmp17)
	}
	return to
}

// AddressToAddress :
func AddressToAddress(from *src.Address) *dst.Address {
	to := &dst.Address{}
	to.Address = &(from.Address)
	return to
}

// SkillToSkill :
func SkillToSkill(from *src.Skill) *dst.Skill {
	to := &dst.Skill{}
	tmp18 := (dst.ID)(from.ID)
	to.ID = &(tmp18)
	tmp19 := (string)(from.Name)
	to.Name = &(tmp19)
	return to
}

// SkillManyToSkillMany :
func SkillManyToSkillMany(from []src.Skill) []dst.Skill {
	to := make([]dst.Skill, len(from))
	for i := range from {
		tmp20 := SkillToSkill(&(from[i]))
		if tmp20 != nil {
			tmp21 := *(tmp20)
			to[i] = tmp21
		}
	}
	return to
}

// SkillManyToSkillRefMany :
func SkillManyToSkillRefMany(from []src.Skill) []*dst.Skill {
	to := make([]*dst.Skill, len(from))
	for i := range from {
		to[i] = SkillToSkill(&(from[i]))
	}
	return to
}
