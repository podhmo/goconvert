import (
	bson "gopkg.in/mgo.v2/bson"
)

// EmptyUser : creates empty User
func EmptyUser() User {
	value := User {
		ID: bson.NewObjectId(),
	}
	// FacebookAuthID is *bson.ObjectId
	// GithubAuthID is *bson.ObjectId
	// GoogleAuthID is *bson.ObjectId
	// TwitterAuthID is *bson.ObjectId
	return value
}

// User : creates User with modify function
func User(modify func(value *User)) *User {
	value := EmptyUser()
	modify(&value)
	return &value
}

// EmptySkill : creates empty Skill
func EmptySkill() Skill {
	value := Skill {
		ID: bson.NewObjectId(),
	}
	return value
}

// Skill : creates Skill with modify function
func Skill(modify func(value *Skill)) *Skill {
	value := EmptySkill()
	modify(&value)
	return &value
}

// EmptyFacebookAuth : creates empty FacebookAuth
func EmptyFacebookAuth() FacebookAuth {
	value := FacebookAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// FacebookAuth : creates FacebookAuth with modify function
func FacebookAuth(modify func(value *FacebookAuth)) *FacebookAuth {
	value := EmptyFacebookAuth()
	modify(&value)
	return &value
}

// EmptyGoogleAuth : creates empty GoogleAuth
func EmptyGoogleAuth() GoogleAuth {
	value := GoogleAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// GoogleAuth : creates GoogleAuth with modify function
func GoogleAuth(modify func(value *GoogleAuth)) *GoogleAuth {
	value := EmptyGoogleAuth()
	modify(&value)
	return &value
}

// EmptyTwitterAuth : creates empty TwitterAuth
func EmptyTwitterAuth() TwitterAuth {
	value := TwitterAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// TwitterAuth : creates TwitterAuth with modify function
func TwitterAuth(modify func(value *TwitterAuth)) *TwitterAuth {
	value := EmptyTwitterAuth()
	modify(&value)
	return &value
}

// EmptyGithubAuth : creates empty GithubAuth
func EmptyGithubAuth() GithubAuth {
	value := GithubAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// GithubAuth : creates GithubAuth with modify function
func GithubAuth(modify func(value *GithubAuth)) *GithubAuth {
	value := EmptyGithubAuth()
	modify(&value)
	return &value
}
