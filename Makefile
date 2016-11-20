json:
	go-structjson -target example/src | sed "s@`pwd`/example@..@g;s@$$GOPATH@GOPATH:/@g;s@vert/example/src@github.com/podhmo/hmm/src@g" > example/json/src.json
	go-structjson -target example/dst | sed "s@`pwd`/example@..@g;s@$$GOPATH@GOPATH:/@g" > example/json/dst.json

example:
	python example/example/00load.py --src example/json/src.json > example/example/00load.output.go
	python example/example/01testdata.py --src example/json/src.json --src-package src --package testdata > example/example/01testdata.output.go
	python example/example/02separated.py --src example/json/src.json --src-package src --package testdata --dst example/example/02separated_output/testdata

all: json example

.PHONY: json example
