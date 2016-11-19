json:
	go-structjson -target example/src | sed "s@`pwd`/example@..@g" | sed "s@$$GOPATH@GOPATH:/@g" > example/json/src.json
	go-structjson -target example/dst | sed "s@`pwd`/example@..@g" | sed "s@$$GOPATH@GOPATH:/@g" > example/json/dst.json

example:
	python example/example/00load.py --src example/json/src.json > example/example/00load.output.go

all: json example

.PHONY: json example
