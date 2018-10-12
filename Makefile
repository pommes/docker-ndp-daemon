# Starts app on test server.
# host: user@host
# host_dir: src/python/docker-ndp-proxy/app
int-test:
	ssh $(host) "cd $(host_dir) && python3 main.py"

clean:
	rm -fr target/*

# Creates release package.
# release_version: v1-beta.1 / v1.0 / v1.0.1 / v 1.1-beta.2
target_dir  = ./target
root_name   = docker-ndp-daemon
release_dir = $(target_dir)/$(root_name)
release: clean
	mkdir -p $(release_dir)
	rsync -av --progress . $(release_dir) \
	  --exclude target \
	  --exclude .git \
	  --exclude .github \
	  --exclude .gitignore \
	  --exclude .idea
	gsed -i "s/> Release.*/> Release $(release_version)/" $(release_dir)/README.md
	cd target && tar cvzf $(root_name)-$(release_version).tgz $(root_name)
	cd target && zip -r $(root_name)-$(release_version).zip $(root_name)
