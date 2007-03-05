# TODO
# - make build with java 1.6
#
# Conditional build:
%bcond_without	binary		# do not use binary jar, but compile (needs java < 1.6)
#
%define		_ver	%(echo %{version} | tr . _)
Summary:	SQL relational database engine written in Java
Summary(pl.UTF-8):	Silnik relacyjnych baz danych SQL napisany w Javie
Name:		hsqldb
Version:	1.8.0.7
Release:	0.7
License:	BSD Style
Group:		Development/Languages/Java
Source0:	http://dl.sourceforge.net/hsqldb/%{name}_%{_ver}.zip
# Source0-md5:	d7ae87f80599e740c2590cd43341c075
Source1:	%{name}-standard.cfg
Source2:	%{name}-standard-server.properties
Source3:	%{name}-standard-webserver.properties
Source4:	%{name}-standard-sqltool.rc
Patch0:		%{name}-scripts.patch
Patch1:		%{name}-pld.patch
URL:		http://www.hsqldb.org/
BuildRequires:	ant
BuildRequires:	jdk
BuildRequires:	jpackage-utils >= 0:1.5
BuildRequires:	rpmbuild(macros) >= 1.300
%if %{without binary}
BuildRequires:	jdk < 1.6
BuildRequires:	junit
BuildRequires:	servletapi4
%endif
BuildArch:	noarch
ExclusiveArch:	i586 i686 pentium3 pentium4 athlon %{x8664} noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
HSQLDB is the leading SQL relational database engine written in Java.
It has a JDBC driver and supports a rich subset of ANSI-92 SQL (BNF
tree format) plus SQL 99 and 2003 enhancements. It offers a small
(less than 100k in one version for applets), fast database engine
which offers both in-memory and disk-based tables and supports
embedded and server modes.

Additionally, it includes tools such as a minimal web server,
in-memory query and management tools (can be run as applets) and a
number of demonstration examples.

%description -l pl.UTF-8
HSQLDB to wiodący silnik relacyjnych baz danych SQL napisany w Javie.
Ma sterownik JDBC i obsługuje znaczny podzbiór ANSI-92 SQL (w formacie
drzew BNF) oraz rozszerzenia SQL 99 i 2003. Oferuje mały (poniżej 100k
w jednej wersji dla apletów), szybki silnik obsługujący tabele zarówno
w pamięci, jak i na dysku; obsługuje tryb wbudowany oraz serwerowy.

Ponadto zawiera narzędzia takie jak minimalny serwer WWW, zapytania w
pamięci i narzędzia zarządzające (mogące działać jako aplety) oraz
wiele przykładów demonstracyjnych.

%package manual
Summary:	Manual for HSQLDB
Summary(pl.UTF-8):	Podręcznik do HSQLDB
Group:		Development/Languages/Java

%description manual
Documentation for HSQLDB.

%description manual -l pl.UTF-8
Podręcznik do HSQLDB.

%package javadoc
Summary:	Javadoc for HSQLDB
Summary(pl.UTF-8):	Dokumentacja javadoc do HSQLDB
Group:		Development/Languages/Java
Requires:	jpackage-utils

%description javadoc
Javadoc for HSQLDB.

%description javadoc -l pl.UTF-8
Dokumentacja javadoc do HSQLDB.

%package demo
Summary:	Demo for HSQLDB
Summary(pl.UTF-8):	Pliki demonstracyjne dla HSQLDB
Group:		Development/Languages/Java
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description demo
Demonstrations and samples for HSQLDB.

%description demo -l pl.UTF-8
Programy demonstracyjne i przykładowe dla HSQLDB.

%package server
Summary:	HSQLDB server
Group:		Applications/Databases
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	rc-scripts
Requires:	servletapi4
Provides:	group(hsqldb)
Provides:	user(hsqldb)
Conflicts:	%{name} < 1.8.0.7-0.4

%description server
HSQLDB server.

%prep
%setup -q -n %{name}
%patch0 -p0
%patch1 -p1

# remove all binary libs
%{!?with_binary:rm -f lib/hsqldb.jar}
rm -f lib/servlet.jar

cp -a doc manual
rm -rf manual/src
cp -a index.html manual

%build
export CLASSPATH=\
%if %{without binary}
$(build-classpath \
	jsse/jsse \
	jsse/jnet \
	jsse/jcert \
	java/jdbc-stdext \
	servletapi4 \
	junit \
)
%endif

cd build
%ant %{!?with_binary:jar} javadoc

%install
rm -rf $RPM_BUILD_ROOT
# jar
install -d $RPM_BUILD_ROOT%{_javadir}
install lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
ln -s  %{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# bin
install -d $RPM_BUILD_ROOT%{_bindir}
install bin/runUtil.sh $RPM_BUILD_ROOT%{_bindir}/%{name}RunUtil

# sysv init
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install bin/%{name} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

# config
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

# serverconfig
install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/server.properties
install %{SOURCE3} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/webserver.properties
install %{SOURCE4} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/sqltool.rc
# lib
install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/lib
install lib/functions 	$RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/lib
# data
install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/data
# demo
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/demo
install demo/*.sh 	$RPM_BUILD_ROOT%{_datadir}/%{name}/demo
install demo/*.html 	$RPM_BUILD_ROOT%{_datadir}/%{name}/demo

# javadoc
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -a doc/src/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%pre server
%groupadd -g 169 %{name}
%useradd -u 169 -g %{name} -s /bin/sh -d %{_localstatedir}/lib/%{name} %{name}

%post server
ln -sf $(build-classpath servletapi4) %{_localstatedir}/lib/%{name}/lib/servlet.jar
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun server
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun server
if [ "$1" = "0" ]; then
	rm -f %{_localstatedir}/lib/%{name}/lib/servlet.jar
	%userremove %{name}
	%groupremove %{name}
fi

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%preun javadoc
if [ "$1" = "0" ]; then
	rm -f %{_javadocdir}/%{name}
fi

%files
%defattr(644,root,root,755)
%doc doc/hsqldb_lic.txt
%{_javadir}/*

%files manual
%defattr(644,root,root,755)
%doc manual/*

%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}-%{version}

%files demo
%defattr(644,root,root,755)
%{_datadir}/%{name}

%files server
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %{_localstatedir}/lib/%{name}
%attr(755,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/data
%{_localstatedir}/lib/%{name}/lib
%{_localstatedir}/lib/%{name}/server.properties
%{_localstatedir}/lib/%{name}/webserver.properties
%attr(600,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/sqltool.rc
