%define		_ver	%(echo %{version} | tr . _)
Summary:	SQL relational database engine written in Java
Name:		hsqldb
Version:	1.8.0.7
Release:	0.1
License:	BSD Style
URL:		http://www.hsqldb.org/
Source0:	http://dl.sourceforge.net/hsqldb/%{name}_%{_ver}.zip
# Source0-md5:	d7ae87f80599e740c2590cd43341c075
Source1:	%{name}-standard.cfg
Source2:	%{name}-standard-server.properties
Source3:	%{name}-standard-webserver.properties
Source4:	%{name}-standard-sqltool.rc
Patch0:		%{name}-scripts.patch
#Patch1: %{name}-build_xml.patch
Group:		Development/Languages/Java
BuildRequires:	ant
BuildRequires:	jdk
BuildRequires:	jpackage-utils >= 0:1.5
BuildRequires:	junit
BuildRequires:	rpmbuild(macros) >= 1.300
BuildRequires:	servletapi4
Requires:	servletapi4
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

%package manual
Summary:	Manual for %{name}
Group:		Development/Languages/Java

%description manual
Documentation for %{name}.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Languages/Java

%description javadoc
Javadoc for %{name}.

%package demo
Summary:	Demo for %{name}
Group:		Development/Languages/Java
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -q -T -c -n %{name}
(cd ..
unzip -q %{SOURCE0}
)

# set right permissions
find . -name "*.sh" -exec chmod 755 \{\} \;
# remove all _notes directories
for dir in `find . -name _notes`; do rm -rf $dir; done
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
find . -name "*.class" -exec rm -f {} \;
find . -name "*.war" -exec rm -f {} \;

# correct silly permissions
chmod -R go=u-w *

%patch0
#%patch1

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

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} ${jar/-%{version}/}; done)

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
cp -r doc/src/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
# FIXME: re-entrancy
rm -rf doc/src

# manual
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/doc
cp -r doc/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp index.html $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "hsqldb" user and group
# we need a shell to be able to use su - later
%{_sbindir}/groupadd %{name} 2> /dev/null || :
%{_sbindir}/useradd -g %{name} \
    -s /bin/sh -d %{_localstatedir}/lib/%{name} %{name} 2> /dev/null || :

%post
rm -f %{_localstatedir}/lib/%{name}/lib/hsqldb.jar
rm -f %{_localstatedir}/lib/%{name}/lib/servlet.jar
(cd %{_localstatedir}/lib/%{name}/lib
    ln -s $(build-classpath hsqldb) hsqldb.jar
    ln -s $(build-classpath servletapi4) servlet.jar
)

%preun
if [ "$1" = "0" ]; then
	rm -f %{_localstatedir}/lib/%{name}/lib/hsqldb.jar
	rm -f %{_localstatedir}/lib/%{name}/lib/servlet.jar
	%{_sbindir}/userdel %{name} >> /dev/null 2>&1 || :
	%{_sbindir}/groupdel %{name} >> /dev/null 2>&1 || :
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
%doc %{_docdir}/%{name}-%{version}/hsqldb_lic.txt
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
%doc doc/*

%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}-%{version}

%files demo
%defattr(644,root,root,755)
%{_datadir}/%{name}
