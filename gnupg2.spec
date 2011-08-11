Summary: Utility for secure communication and data storage
Name:    gnupg2
Version: 2.0.14
Release: 4%{?dist}

License: GPLv3+
Group:   Applications/System
Source0: ftp://ftp.gnupg.org/gcrypt/%{?pre:alpha/}gnupg/gnupg-%{version}%{?pre}.tar.bz2
Source1: ftp://ftp.gnupg.org/gcrypt/%{?pre:alpha/}gnupg/gnupg-%{version}%{?pre}.tar.bz2.sig
# svn export svn://cvs.gnupg.org/gnupg/trunk gnupg2; tar cjf gnupg-<date>svn.tar.bz2 gnupg2
#Source0: gnupg2-20090809svn.tar.bz2
Patch1:  gnupg-2.0.13-insttools.patch
Patch2:  gnupg-2.0.14-tests-s2kcount.patch
Patch3:  gnupg-2.0.14-secmem.patch
Patch4:  gnupg-2.0.14-cve-2010-2547.patch

URL:     http://www.gnupg.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#BuildRequires: automake libtool texinfo transfig
BuildRequires: bzip2-devel
BuildRequires: curl-devel
BuildRequires: docbook-utils
BuildRequires: gettext
BuildRequires: libassuan-static, libassuan-devel >= 1.0.4
# libgcrypt-devel >= 1.4.0 is preferred, see http://bugzilla.redhat.com/435320
BuildRequires:  libgcrypt-devel >= 1.4
BuildRequires: libgpg-error-devel => 1.4
BuildRequires: libksba-devel >= 1.0.2
BuildRequires: openldap-devel
BuildRequires: libusb-devel
BuildRequires: pcsc-lite-libs
BuildRequires: pth-devel
BuildRequires: readline-devel ncurses-devel
BuildRequires: zlib-devel

Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info
Requires(hint): pinentry

# pgp-tools, perl-GnuPG-Interface requires 'gpg' (not sure why) -- Rex
Provides: gpg = %{version}-%{release}
# Obsolete GnuPG-1 package
Provides: gnupg = %{version}-%{release}
Obsoletes: gnupg <= 1.4.10

%package smime
Summary: CMS encryption and signing tool and smart card support for GnuPG
Requires: gnupg2 = %{version}-%{release}
Group: Applications/Internet
Requires(hint): dirmngr


%description
GnuPG is GNU's tool for secure communication and data storage.  It can
be used to encrypt data and to create digital signatures.  It includes
an advanced key management facility and is compliant with the proposed
OpenPGP Internet standard as described in RFC2440 and the S/MIME
standard as described by several RFCs.

GnuPG 2.0 is a newer version of GnuPG with additional support for
S/MIME.  It has a different design philosophy that splits
functionality up into several modules. The S/MIME and smartcard functionality
is provided by the gnupg2-smime package.

%description smime
GnuPG is GNU's tool for secure communication and data storage. This
package adds support for smart cards and S/MIME encryption and signing
to the base GnuPG package 

%prep
%setup -q -n gnupg-%{version}

%patch1 -p1 -b .insttools
%patch2 -p1 -b .s2k
%patch3 -p1 -b .secmem
%patch4 -p1 -b .x509-realloc

# pcsc-lite library major: 0 in 1.2.0, 1 in 1.2.9+ (dlopen()'d in pcsc-wrapper)
# Note: this is just the name of the default shared lib to load in scdaemon,
# it can use other implementations too (including non-pcsc ones).
%global pcsclib %(basename $(ls -1 %{_libdir}/libpcsclite.so.? 2>/dev/null ) 2>/dev/null )

sed -i -e 's/"libpcsclite\.so"/"%{pcsclib}"/' scd/{scdaemon,pcsc-wrapper}.c

# fix temp broken docs
#sed -i -e 's/^@include version.texi//' doc/gnupg.texi
#./autogen.sh


%build

%configure \
  --disable-rpath

# need scratch gpg database for tests
mkdir -p $HOME/.gnupg

# not smp-safe
make


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} \
  INSTALL="install -p" \
  docdir=%{_docdir}/%{name}-%{version}

%find_lang %{name}

# gpgconf.conf
mkdir -p %{buildroot}%{_sysconfdir}/gnupg
touch %{buildroot}%{_sysconfdir}/gnupg/gpgconf.conf

# more docs
install -m644 -p AUTHORS COPYING ChangeLog NEWS THANKS TODO \
  %{buildroot}%{_docdir}/%{name}-%{version}/

# compat symlinks
ln -sf gpg2 %{buildroot}%{_bindir}/gpg
ln -sf gpgv2 %{buildroot}%{_bindir}/gpgv
ln -sf gpg2.1 %{buildroot}%{_mandir}/man1/gpg.1
ln -sf gpgv2.1 %{buildroot}%{_mandir}/man1/gpgv.1


# info dir
rm -f %{buildroot}%{_infodir}/dir


%check
# need scratch gpg database for tests
mkdir -p $HOME/.gnupg
# some gpg2 tests (still) FAIL on non i386 platforms
make -k check


%post
/sbin/install-info %{_infodir}/gnupg.info %{_infodir}/dir ||:

%preun
if [ $1 -eq 0 ]; then
  /sbin/install-info --delete %{_infodir}/gnupg.info %{_infodir}/dir ||:
fi


%files -f %{name}.lang
%defattr(-,root,root,-)
#doc AUTHORS COPYING ChangeLog NEWS README THANKS TODO
%{_docdir}/%{name}-%{version}/
%dir %{_sysconfdir}/gnupg
%ghost %config(noreplace) %{_sysconfdir}/gnupg/gpgconf.conf
## docs say to install suid root, but fedora/rh security folk say not to
#attr(4755,root,root) %{_bindir}/gpg2
%{_bindir}/gpg2
%{_bindir}/gpgv2
%{_bindir}/gpg
%{_bindir}/gpgv
%{_bindir}/gpg-connect-agent
%{_bindir}/gpg-agent
%{_bindir}/gpgconf
%{_bindir}/gpgkey2ssh
%{_bindir}/gpgparsemail
%{_bindir}/gpgsplit
%{_bindir}/gpg-zip
%{_bindir}/watchgnupg
%{_sbindir}/*
%{_datadir}/gnupg/
%{_libexecdir}/*
%{_infodir}/*.info*
%{_mandir}/man?/*
%exclude %{_datadir}/gnupg/com-certs.pem
%exclude %{_mandir}/man?/gpgsm*
%exclude %{_mandir}/man?/scdaemon*

%files smime
%defattr(-,root,root,-)
%{_bindir}/gpgsm*
%{_bindir}/kbxutil
%{_bindir}/scdaemon
%{_mandir}/man?/gpgsm*
%{_mandir}/man?/scdaemon*
%{_datadir}/gnupg/com-certs.pem

%clean
rm -rf %{buildroot}


%changelog
* Mon Aug  2 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-4
- fix use after free when importing certain X509 certificates
  CVE-2010-2547 (#618156)

* Fri Jun 18 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-3
- initialize small amount of secmem for list of algorithms in help (#598847)
  (necessary in the FIPS mode of libgcrypt)

* Tue Feb  9 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-2
- disable selinux support - it is too rudimentary and restrictive (#562982)

* Mon Jan 11 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-1
- new upstream version
- fix a few tests so they do not need to execute gpg-agent

* Tue Dec  8 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.0.13-4
- Explicitly BR libassuan-static in accordance with the Packaging
  Guidelines (libassuan-devel is still static-only).

* Fri Oct 23 2009 Tomas Mraz <tmraz@redhat.com> - 2.0.13-3
- drop s390 specific ifnarchs as all the previously missing dependencies
  are now there
- split out gpgsm into a smime subpackage to reduce main package dependencies

* Wed Oct 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.0.13-2
- provide/obsolete gnupg-1 and add compat symlinks to be able to drop
  gnupg-1

* Fri Sep 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.13-1
- gnupg-2.0.13
- Unable to use gpg-agent + input methods (#228953)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 17 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.12-1
- gnupg-2.0.12

* Wed Mar 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.11-1
- gnupg-2.0.11

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 31 2009 Karsten Hopp <karsten@redhat.com> 2.0.10-1
- don't require pcsc-lite-libs and libusb on mainframe where
  we don't have those packages as there's no hardware for that

* Tue Jan 13 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.10-1
- gnupg-2.0.10

* Mon Aug 04 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.9-3
- workaround rpm quirks 

* Sat May 24 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.9-2
- Patch from upstream to fix curl 7.18.1+ and gcc4.3+ compile error

* Mon May 19 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.9-1.1
- minor release bump for sparc rebuild

* Wed Mar 26 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.9-1
- gnupg2-2.0.9
- drop Provides: openpgp
- versioned Provides: gpg
- own %%_sysconfdir/gnupg

* Fri Feb 08 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.8-3 
- respin (gcc43)

* Wed Jan 23 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.8-2
- avoid kde-filesystem dep (#427316)

* Thu Dec 20 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.8-1
- gnupg2-2.0.8

* Mon Dec 17 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.8-0.1.rc1
- gnupg2-2.0.8rc1

* Tue Dec 04 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-5
- respin for openldap

* Mon Nov 12 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-4
- Requires: kde-filesystem (#377841)

* Wed Oct 03 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-3
- %%build: (re)add mkdir -p $HOME/.gnupg

* Wed Oct 03 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-2
- Requires: dirmngr (#312831)

* Mon Sep 10 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-1
- gnupg-2.0.7

* Fri Aug 24 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.6-2
- respin (libassuan)

* Thu Aug 16 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.6-1
- gnupg-2.0.6
- License: GPLv3+

* Thu Aug 02 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.5-4
- License: GPLv3

* Mon Jul 16 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.5-3
- 2.0.5 too many open files fix

* Fri Jul 06 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.5-2
- gnupg-2.0.5
- gpg-agent not restarted after kde session crash/killed (#196327)
- BR: libassuan-devel > 1.0.2, libksba-devel > 1.0.2

* Fri May 18 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.4-1
- gnupg-2.0.4

* Thu Mar 08 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.3-1
- gnupg-2.0.3

* Fri Feb 02 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.2-1
- gnupg-2.0.2

* Wed Dec 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.1-2
- CVE-2006-6235 (#219934)

* Wed Nov 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.1-1
- gnupg-2.0.1
- CVE-2006-6169 (#217950)

* Sat Nov 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.1-0.3.rc1
- gnupg-2.0.1rc1 

* Thu Nov 16 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.0-4
- update %%description
- drop dearmor patch

* Mon Nov 13 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.0-3
- BR: libassuan-static >= 1.0.0

* Mon Nov 13 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.0-2
- gnupg-2.0.0

* Fri Nov 10 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.95-3
- upstream 64bit patch

* Mon Nov 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.95-2
- fix (more) file conflicts with gnupg

* Mon Nov 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.95-1
- 1.9.95

* Wed Oct 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.94-1
- 1.9.94

* Wed Oct 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.93-1
- 1.9.93

* Wed Oct 11 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.92-2
- fix file conflicts with gnupg

* Wed Oct 11 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.92-1
- 1.9.92

* Tue Oct 10 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.91-4
- make check ||: (apparently checks return err even on success?)

* Tue Oct 10 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.91-3
- --enable-selinux-support
- x86_64: --disable-optimization (to avoid gpg2 segfaults), for now

* Thu Oct 05 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.91-1
- 1.9.91

* Wed Oct 04 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-8
- respin

* Tue Sep 26 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.90-1
- 1.9.90 (doesn't build, not released)

* Mon Sep 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.23-1
- 1.9.23 (doesn't build, not released)

* Mon Sep 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-7
- gpg-agent-startup.sh: fix case where valid .gpg-agent-info exists

* Mon Sep 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-6
- fix "syntax error in gpg-agent-startup.sh" (#206887)

* Thu Sep 07 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-3
- fc6 respin (for libksba-1.0)

* Tue Aug 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-2
- fc6 respin

* Fri Jul 28 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-1
- 1.9.22

* Thu Jun 22 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.21-3
- fix "gpg-agent not restarted after kde session crash/killed (#196327)

* Thu Jun 22 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.21-2
- 1.9.21
- omit gpg2 binary to address CVS-2006-3082 (#196190)

* Mon Mar  6 2006 Ville Skyttä <ville.skytta at iki.fi>> 1.9.20-3
- Don't hardcode pcsc-lite lib name (#184123)

* Thu Feb 16 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.20-2
- fc4+: use /etc/kde/(env|shutdown) for scripts (#175744)

* Fri Feb 10 2006 Rex Dieter <rexdieter[AT]users.sf.net>
- fc5: gcc/glibc respin

* Tue Dec 20 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.20-1
- 1.9.20

* Thu Dec 01 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-8
- include gpg-agent-(startup|shutdown) scripts (#136533)
- BR: libksba-devel >= 1.9.12 
- %%check: be permissive about failures (for now)

* Wed Nov 30 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-3
- BR: libksba-devel >= 1.9.13

* Tue Oct 11 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-2
- back to BR: libksba-devel = 1.9.11

* Tue Oct 11 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-1
- 1.9.19

* Fri Aug 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-9
- configure: NEED_KSBA_VERSION=0.9.12 -> 0.9.11

* Fri Aug 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-7
- re-enable 'make check', rebuild against (older) libksba-0.9.11

* Tue Aug  9 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-6
- don't 'make check' by default (regular builds pass, but FC4/5+plague fails)

* Mon Aug  8 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-5
- 1.9.18
- drop pth patch (--enable-gpg build fixed)
- update description (from README)

* Fri Jul  1 2005 Ville Skyttä <ville.skytta at iki.fi> - 1.9.17-1
- 1.9.17, signal info patch applied upstream (#162264).
- Patch to fix lvalue build error with gcc4 (upstream #485).
- Patch scdaemon and pcsc-wrapper to load the versioned (non-devel)
  pcsc-lite lib by default.

* Fri May 13 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.16-3
- Include upstream's patch for signal.c.

* Tue May 10 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.16-1
- Merge changes from Rex's 1.9.16-1 (Thu Apr 21):
-   opensc support unconditional
-   remove hard-coded .gz from %%post/%%postun
-   add %%check section
-   add pth patch
- Put back patch modified from 1.9.15-4 to make tests verbose
  and change signal.c to describe received signals better.

* Sun May  8 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- Drop patch0 again.

* Sun May  8 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.15-4
- Add patch0 temporarily to get some output from failing test.

* Sat May  7 2005 David Woodhouse <dwmw2@infradead.org> 1.9.15-3
- Rebuild.

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Tue Feb  1 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 0:1.9.15-1
- Make install-info in scriptlets less noisy.

* Tue Jan 18 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.15-0.fdr.1
- 1.9.15

* Fri Jan 07 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.14-0.fdr.2
- note patch/hack to build against older ( <1.0) libgpg-error-devel

* Thu Jan 06 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.14-0.fdr.1
- 1.9.14
- enable opensc support
- BR: libassuan-devel >= 0.6.9

* Thu Oct 21 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.4
- remove suid.

* Thu Oct 21 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.3
- remove Provides: newpg

* Wed Oct 20 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.2
- Requires: pinentry
- gpg2 suid
- update description

* Tue Oct 19 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.1
- first try
- leave out opensc support (for now), enable --with-opensc

