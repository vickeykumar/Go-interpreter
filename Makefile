GIT_TOP=$(shell git rev-parse --show-toplevel 2>/dev/null)
UNAME := $(shell uname)
USER = $(shell id -u -n)

install:
	if [ '$(UNAME)' = 'Linux' ] || [ '$(UNAME)' = 'Darwin' ]; then echo "installing for ${USER}"; mkdir -p /tmp/gointerpreter;\
	chown -R ${USER} /tmp/gointerpreter; chmod -R 777 /tmp/gointerpreter; chmod 755 ${GIT_TOP}/gointerpreter.py;\
	 ln -s ${GIT_TOP}/gointerpreter.py /usr/local/bin/gointerpreter; chown -R ${USER} /usr/local/bin/gointerpreter; fi

clean:
	if [ '$(UNAME)' = 'Linux' ]; then echo "cleaning for ${USER}"; rm -f /usr/local/bin/gointerpreter;\
	rm -rf /tmp/gointerpreter; fi
