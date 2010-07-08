PACKAGE_NAME = python-csa
PACKAGE_VERSION = $(shell python -c 'from csa.version import __version__; print __version__')

debdir = dist/csa-$(PACKAGE_VERSION)

.PHONY: dist debian-source debian-package

dist:
	python setup.py sdist

debian-source: dist
	@test ! -e $(debdir) || ( echo "*** Remove directory dist/csa-${PACKAGE_VERSION}" && exit 1 )
	mv dist/csa-$(PACKAGE_VERSION).tar.gz dist/$(PACKAGE_NAME)_$(PACKAGE_VERSION).orig.tar.gz
	( cd dist; tar zxf $(PACKAGE_NAME)_$(PACKAGE_VERSION).orig.tar.gz )
	mkdir $(debdir)/debian
	cp -pr debian $(debdir)

debian-package: debian-source
	( cd $(debdir) && dpkg-buildpackage '-mMikael Djurfeldt <mdj@debian.org>' -rfakeroot && cd ../.. && rm -rf $(debdir) )
