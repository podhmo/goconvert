json:
	go-structjson -target example/src | sed "s@`pwd`/example@..@g;s@$$GOPATH@GOPATH:/@g; s@vert/example@github.com/podhmo/hmm@g" > example/json/src.json
	go-structjson -target example/dst | sed "s@`pwd`/example@..@g;s@$$GOPATH@GOPATH:/@g; s@vert/example@github.com/podhmo/hmm@g" > example/json/dst.json
	go-funcjson -target example/example/03convert_output | sed "s@`pwd`/example@..@g;s@$$GOPATH@GOPATH:/@g; s@vert/example@github.com/podhmo/hmm@g" > example/json/convert.json

example:
	python example/example/00load.py --src example/json/src.json > example/example/00load.output.go
	python example/example/01testdata.py --src example/json/src.json --src-package src --package testdata > example/example/01testdata.output.go
	python example/example/02separated.py --src example/json/src.json --src-package src --package testdata --dst example/example/02separated_output/testdata
	gofmt -w example/example/02*/**/*.go
	python example/example/03convert.py --src example/json/src.json --dst example/json/dst.json --override example/json/convert.json > example/example/03convert_output/autogen_convert.go
	gofmt -w example/example/03*/*.go

all: json example

.PHONY: json example
