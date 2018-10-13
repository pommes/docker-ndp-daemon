# On macos better use gsed instead of sed for being GNU compatible.
sed        = gsed

#####################################################################

# $1: branch
define check_uncommit_changes
	@git diff --quiet \
	  && echo "No local changes found on branch '$1'" \
	  || (>&2 echo "branch '$1' has uncommitted local changes."); exit 1
endef

# Check that given variables are set and all have non-empty values,
# die with an error otherwise.
#
# Params:
#   1. Variable name(s) to test.
#   2. (optional) Error message to print.
check_defined = \
    $(strip $(foreach 1,$1, \
        $(call __check_defined,$1,$(strip $(value 2)))))
__check_defined = \
    $(if $(value $1),, \
      $(error Undefined $1$(if $2, ($2))))

#####################################################################

# Starts app on test server.
# host: user@host
# host_dir: src/python/docker-ndp-proxy/app
int-test:
	$(call check_defined, host host_dir)
	ssh $(host) "cd $(host_dir) && python3 main.py"

clean:
	rm -fr target/*

# Creates a new branch
# release_version: v1-beta.1 / v1.0 / v1.0.1 / v 1.1-beta.2
create-release-branch:
	$(call check_defined, release_version)
	git checkout -b $(release_version)
	$(sed) -i "s/> Release.*/> Release $(release_version)/" $(release_dir)/README.md
	git commit -m "Created release branch '$(release_version)'"
	git push origin $(release_version)

# Creates release package.
# release_version: v1-beta.1 / v1.0 / v1.0.1 / v 1.1-beta.2
target_dir  = ./target
root_name   = docker-ndp-daemon
release_dir = $(target_dir)/$(root_name)
release: merge_back_release_branch clean
	$(call check_defined, release_version)
	mkdir -p $(release_dir)
	rsync -av --progress . $(release_dir) \
	  --exclude target \
	  --exclude .git \
	  --exclude .github \
	  --exclude .gitignore \
	  --exclude .idea
	$(sed) -i "s/> Release.*/> Release $(release_version)/" $(release_dir)/README.md
	cd target && tar cvzf $(root_name)-$(release_version).tgz $(root_name)
	cd target && zip -r $(root_name)-$(release_version).zip $(root_name)

# Merges the release-branch back to master
# release_version: v1-beta.1 / v1.0 / v1.0.1 / v 1.1-beta.2
merge_back_release_branch: check_branches
	$(call check_defined, release_version)
	git checkout master
	git pull origin master
	git merge $(release_branch)
	git push origin master

# Checks the master and passed release-branch for uncommited changes.
# release_version: v1-beta.1 / v1.0 / v1.0.1 / v 1.1-beta.2
check_branches:
	$(call check_defined, release_version)
	git checkout $(release_version)
	$(call check_uncommit_changes,$(release_version))

	git checkout master
	$(call check_uncommit_changes,master)