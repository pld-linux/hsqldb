# TODO
# - make build with java 1.6
%define		_ver	%(echo %{version} | tr . _)
Summary:	SQL relational database engine written in Java
Summary(pl.UTF-8):	Silnik relacyjnych baz danych SQL napisany w Javie
Name:		hsqldb
Version:	1.8.0.7
Release:	0.2
License:	BSD Style
Group:		Development/Languages/Java
Source0:	http://dl.sourceforge.net/hsqldb/%{name}_%{_ver}.zip
# Source0-md5:	d7ae87f80599e740c2590cd43341c075
Source1:	%{name}-standard.cfg
Source2:	%{name}-standard-server.properties
Source3:	%{name}-standard-webserver.properties
Source4:	%{name}-standard-sqltool.rc
Patch0:		%{name}-scripts.patch
#Patch1:	%{name}-build_xml.patch
URL:		http://www.hsqldb.org/
BuildRequires:	ant
BuildRequires:	jdk
BuildRequires:	jpackage-utils >= 0:1.5
BuildRequires:	junit
BuildRequires:	rpmbuild(macros) >= 1.300
BuildRequires:	servletapi4
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	servletapi4
Provides:	group(hsqldb)
Provides:	user(hsqldb)
Buildarch:	noarch
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%prep
%setup -q -n %{name}
%patch0
#%patch1

# remove all binary libs
find . -name '*.jar' -o -name '*.class' -o -name '*.war' | xargs rm -vf

cp -a doc manual
rm -rf manual/src
cp -a index.html manual

%build
export CLASSPATH=$(build-classpath \
	jsse/jsse \
	jsse/jnet \
	jsse/jcert \
	java/jdbc-stdext \
	servletapi4 \
	junit \
)
cd build
%ant jar javadoc

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

%pre
%groupadd -g 169 %{name}
%useradd -u 169 -g %{name} -s /bin/sh -d %{_localstatedir}/lib/%{name} %{name}

%post
ln -sf $(build-classpath hsqldb) %{_localstatedir}/lib/%{name}/lib/hsqldb.jar
ln -sf $(build-classpath servletapi4) %{_localstatedir}/lib/%{name}/lib/servlet.jar

%preun
if [ "$1" = "0" ]; then
	rm -f %{_localstatedir}/lib/%{name}/lib/hsqldb.jar
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
%attr(755,root,root) %{_bindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/data
%{_localstatedir}/lib/%{name}/lib
%{_localstatedir}/lib/%{name}/server.properties
%{_localstatedir}/lib/%{name}/webserver.properties
%attr(600,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/sqltool.rc

%files manual
%defattr(644,root,root,755)
%doc manual/*

%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}-%{version}

%files demo
%defattr(644,root,root,755)
%{_datadir}/%{name}
