%define reltag .Final
%define namedversion %{version}%{reltag}

Name:           mod_cluster-native
Summary:        JBoss mod_cluster for Apache httpd
Version:        1.3.16
Release:        1%{reltag}%{?dist}
Epoch:          0
License:        LGPLv3
Group:          Applications/System
URL:            http://www.jboss.org/

Source0:        https://github.com/modcluster/mod_cluster/archive/%{namedversion}.zip
Source1:        %{name}.conf
Source2:        %{name}.te
Source3:        %{name}.fc

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	httpd-devel
BuildRequires:	apr-devel
BuildRequires:	apr-util-devel
#64 bit natives only on RHEL 8
ExcludeArch:    i686 i386
BuildRequires:	autoconf
BuildRequires:	zip
BuildRequires:  selinux-policy-devel
Requires(post): python3-policycoreutils
Requires(postun): python3-policycoreutils

Requires:   httpd >= 0:2.4.6
Requires:   apr
Requires:   apr-util

%description
JBoss mod_cluster for Apache httpd 2.4.37.

%prep
%setup -q -n mod_cluster-%{namedversion}

%build
%{!?apxs: %{expand: %%define apxs %{_bindir}/apxs}}
%define aplibdir %(%{apxs} -q LIBEXECDIR 2>/dev/null)

pushd native
for i in advertise mod_manager mod_proxy_cluster mod_cluster_slotmem
do
pushd $i
set -e
sh buildconf
./configure --with-apxs="%{apxs}"
make CFLAGS="%{optflags} -fno-strict-aliasing"
popd
done
popd

%install
%{!?apxs: %{expand: %%define apxs %{_bindir}/apxs}}
%define aplibdir %(%{apxs} -q LIBEXECDIR 2>/dev/null)
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}-%{version}
install -d -m 755 $RPM_BUILD_ROOT/%{aplibdir}/
cp -p native/*/*.so ${RPM_BUILD_ROOT}/%{aplibdir}/
install -d -m 755 $RPM_BUILD_ROOT/%{_localstatedir}/cache/mod_cluster

install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/
install -p -m 644 %{SOURCE1} \
        $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/mod_cluster.conf

# for SELinux
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}
mkdir selinux
pushd selinux
    cp -p %{SOURCE2} .
    cp -p %{SOURCE3} .

    make -f %{_datadir}/selinux/devel/Makefile
    install -p -m 644 -D %{name}.pp $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}/mod_cluster.pp
popd

%clean
rm -Rf $RPM_BUILD_ROOT

%post
if [ $1 -eq 1 ] ; then
    %{_sbindir}/semodule -i %{_datadir}/selinux/packages/%{name}/mod_cluster.pp 2>/dev/null || :
    %{_sbindir}/semanage port -a -t http_port_t -p udp 23364 >/dev/null 2>&1 || :
    %{_sbindir}/semanage port -a -t http_port_t -p tcp 6666 >/dev/null 2>&1 || :
    /sbin/restorecon -R /var/cache/mod_cluster >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    %{_sbindir}/semanage port -d -t http_port_t -p udp 23364 2>&1 || :
    %{_sbindir}/semanage port -d -t http_port_t -p tcp 6666 2>&1 || :
    %{_sbindir}/semodule -r mod_cluster >/dev/null 2>&1 || :
    /sbin/restorecon -R /var/cache/mod_cluster >/dev/null 2>&1 || :
fi

%files
%{!?apxs: %{expand: %%define apxs %{_bindir}/apxs}}
%define aplibdir %(%{apxs} -q LIBEXECDIR 2>/dev/null)
%defattr(0644,root,root,0755)
%doc lgpl.txt
%dir %{_localstatedir}/cache/mod_cluster
%attr(0755,root,root) %{aplibdir}/*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/mod_cluster.conf
# for SELinux
%dir %{_datadir}/selinux/packages/%{name}
%{_datadir}/selinux/packages/%{name}/mod_cluster.pp

%changelog
* Tue Mar 22 2022 Ricardo Arguello <ricardo.arguello@gmail.com> - 1.3.16-1.Final
- Upgrade to mod_cluster 1.3.16

* Tue Oct 6 2020 Ricardo Arguello <ricardo.arguello@gmail.com> - 1.3.14-2.Final
- Rebuild for EL8

* Mon May 11 2020 Mladen Turk <mturk@redhat.com> - 1.3.14-1.Final
- Upgrade to mod_cluster 1.3.14

* Thu Aug 08 2019 Yaakov Selkowitz <yselkowi@redhat.com> - 1.3.11-2
- Rebuilt for multiple architectures

* Thu Jun 27 2019 Petros Marios Prokopiou <pprokopi@redhat.com> - 1.3.11-2
- Applied fix for [JBCS-405]

* Wed Jun 19 2019 Hui Wang <huwang@redhat.com> - 1.3.11-2
- Build with new httpd 2.4.37

* Wed Jun 19 2019 Hui Wang <huwang@redhat.com> - 1.3.11-1
- Build with new httpd 2.4.37

* Wed Jun 05 2019 Petros Marios Prokopiou <pprokopi@redhat.com> - 1.3.11-1
- Updating to mod_cluster 1.3.11 [JBCS-446]

* Thu Nov 01 2018 Sokratis Zappis <szappis@redhat.com> - 1.3.8-3
- Build for JBCS httpd 2.4.29 SP1 DR1

* Tue Mar 06 2018 Hui Wang <huwang@redhat.com> - 1.3.8-1
- Build with the latest commitId

* Tue Mar 06 2018 Jean-Frederic Clere <jclere@redhat.com> - 1.3.8-1
- retrying...

* Mon Mar 05 2018 Georgios Zaronikas Karagiannis <gzaronik@redhat.com> - 1.3.8-1
- Build with httpd 2.4.29

* Mon Mar 05 2018 Jean-Frederic Clere <jclere@redhat.com> - 1.3.8-1
- Adjust to the new git repo.

* Tue Nov 07 2017 Georgios Zaronikas Karagiannis <gzaronik@redhat.com> - 1.3.8-14
- Updating to 1.3.8

* Tue Nov 07 2017 George Zaronikas <gzaronik@redhat.com> - 1.3.8-1
- Updating to mod_cluster 1.3.8

* Tue Feb 07 2017 Jan Fnukal <hfnukal@redhat.com> - 1.3.5-14
- jbcs-httpd24 SP1

* Wed Oct 26 2016 Hui Wang <huwang@redhat.com> - 1.3.5-13
- Rebuild

* Wed Oct 26 2016 Jean-Frederic Clere <jclere@redhat.com> - 1.3.5-12
-

* Wed Oct 26 2016 Jean-Frederic Clere <jfclere@redhat.com> - 1.3.5-0
- 1.3.5.Final-redhat

* Fri Oct 21 2016 Permaine Cheung <pcheung@redhat.com> - 1.3.4-12
- 1.3.4.Final-redhat-1

* Wed Sep 28 2016 Coty Sutherland <csutherl@redhat.com> - 1.3.3-12
- Resolves: JBCS-167 mod_cluster-native uses /var/cache/mod_cluster instead of /opt/rh/jbcs-httpd24/root/var/cache/mod_cluster
- Resolves: JBCS-172 Update mod_cluster-native selinux policy

* Wed Jul 20 2016 Permaine Cheung <pcheung@redhat.com> - 1.3.3-11
- 1.3.3.Final-redhat-1

* Wed Jul 20 2016 Permaine Cheung <pcheung@redhat.com> - 1.3.3-1.Final-redhat-1
- 1.3.3

* Tue Feb 16 2016 Fernando Nasser <fnasser@redhat.com> - 1.3.1-10
- Build from source-repos

* Fri Feb 12 2016 Fernando Nasser <fnasser@redhat.com> - 1.3.1-9
- JCSP-24 postun scriptlet fails when unistalling mod_cluster-native

* Tue Dec 22 2015 Fernando Nasser <fnasser@redhat.com> - 0:1.3.1-7
- Build in the jbcs-httpd24 collection

* Tue Oct 20 2015 Permaine Cheung <pcheung@redhat.com> - 0:1.3.1-6.Final-redhat-2
- Rebuild

* Fri Apr 10 2015 Permaine Cheung <pcheung@redhat.com> - 0:1.3.1-5.Final-redhat-2
- 1.3.1.Final-redhat-2
- Remove patch for CVE-2015-0298 as it has been incorporated in the new tag

* Wed Mar 18 2015 Dustin Kut Moy Cheung <dcheung@redhat.com> - 0:1.3.1-4.Beta2-redhat-1
- add patch for CVE-2015-0298

* Mon Jan 26 2015 Permaine Cheung <pcheung@redhat.com> - 0:1.3.1-3.Beta1-redhat-1
- 1.3.1.Beta2-redhat-1

* Thu Dec 18 2014 Weinan Li <weli@redhat.com> - 0:1.3.1-2.Beta1
- Fix conf file

* Tue Nov 18 2014 Permaine Cheung <pcheung@redhat.com> - 0:1.3.1-1.Beta1
- 1.3.1.Beta1
- JWS 3.0 build
