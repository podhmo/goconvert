package testdata

import (
	src "github.com/podhmo/hmm/src"
	bson "gopkg.in/mgo.v2/bson"
)

// EmptyFacebookAuth : creates empty FacebookAuth
func EmptyFacebookAuth() src.FacebookAuth {
	value := src.FacebookAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// FacebookAuth : creates FacebookAuth with modify function
func FacebookAuth(modify func(value *src.FacebookAuth)) *src.FacebookAuth {
	value := EmptyFacebookAuth()
	modify(&value)
	return &value
}

// EmptyGithubAuth : creates empty GithubAuth
func EmptyGithubAuth() src.GithubAuth {
	value := src.GithubAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// GithubAuth : creates GithubAuth with modify function
func GithubAuth(modify func(value *src.GithubAuth)) *src.GithubAuth {
	value := EmptyGithubAuth()
	modify(&value)
	return &value
}

// EmptyGoogleAuth : creates empty GoogleAuth
func EmptyGoogleAuth() src.GoogleAuth {
	value := src.GoogleAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// GoogleAuth : creates GoogleAuth with modify function
func GoogleAuth(modify func(value *src.GoogleAuth)) *src.GoogleAuth {
	value := EmptyGoogleAuth()
	modify(&value)
	return &value
}

// EmptyTwitterAuth : creates empty TwitterAuth
func EmptyTwitterAuth() src.TwitterAuth {
	value := src.TwitterAuth {
		Id: bson.NewObjectId(),
		UserId: bson.NewObjectId(),
	}
	return value
}

// TwitterAuth : creates TwitterAuth with modify function
func TwitterAuth(modify func(value *src.TwitterAuth)) *src.TwitterAuth {
	value := EmptyTwitterAuth()
	modify(&value)
	return &value
}