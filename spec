Name: @PACKAGE@
Summary: Web browser for ezmlm-idx archives
Version: @VERSION@
Release: 1
Copyright: GPL
Group: Applications/Internet
Source: http://untroubled.org/@PACKAGE@/@PACKAGE@-@VERSION@.tar.gz
BuildRoot: %{_tmppath}/@PACKAGE@-buildroot
#BuildArch: noarch
URL: http://untroubled.org/@PACKAGE@/
Packager: Bruce Guenter <bruceg@em.ca>

%description
ezmlm-browse is a web browser for ezmlm-idx archives.  Its presentation
of those archives is template driven, allowing for a completely
customizeable look-and-feel.

%prep
%setup

%build
#make CFLAGS="%{optflags}" all
echo gcc "%{optflags}" >conf-cc
echo gcc -s >conf-ld
echo %{_bindir} >conf-bin
make

%install
rm -fr %{buildroot}
#make install_prefix=%{buildroot} bindir=%{_bindir} mandir=%{_mandir} install
rm -f installer.o installer instcheck
echo %{buildroot}%{_bindir} >conf-bin
make installer instcheck

mkdir -p %{buildroot}%{_bindir}
./installer

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ANNOUNCEMENT COPYING NEWS README *.html
%{_bindir}/*
