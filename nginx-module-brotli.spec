#
%define nginx_user nginx
%define nginx_group nginx

%if 0%{?rhel} || 0%{?amzn} || 0%{?fedora}
%define _group System Environment/Daemons
%if 0%{?amzn} == 2
BuildRequires: openssl11-devel
%else
BuildRequires: openssl-devel
%endif
%endif

%if 0%{?suse_version} >= 1315
%define _group Productivity/Networking/Web/Servers
BuildRequires: libopenssl-devel
%define _debugsource_template %{nil}
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 0)
%define epoch 1
Epoch: %{epoch}
%define dist .el7
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 2)
%define epoch 1
Epoch: %{epoch}
%endif

%if 0%{?rhel} == 8
%define epoch 1
Epoch: %{epoch}
%define _debugsource_template %{nil}
%endif

%if 0%{?rhel} == 9
%define epoch 1
Epoch: %{epoch}
%define _debugsource_template %{nil}
%endif

%if 0%{?fedora}
%define _debugsource_template %{nil}
%global _hardened_build 1
%endif

%define base_version 1.23.1
%define base_release 1%{?dist}.ngx

%define bdir %{_builddir}/%{name}-%{base_version}

Summary: nginx Brotli dynamic modules
Name: nginx-module-brotli
Version: %{base_version}
Release: %{base_release}
Vendor: Eugene Wu <kuretru@gmail.com>
URL: https://github.com/kuretru/nginx-module-brotli
Group: %{_group}

Source0: https://nginx.org/download/nginx-%{base_version}.tar.gz
Source1: COPYRIGHT
Source2: ngx_brotli-1.0.9.tar.gz

License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{base_version}-%{base_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre2-devel
Requires: nginx-r%{base_version}
Provides: %{name}-r%{base_version}

%description
nginx Brotli dynamic modules.

%if 0%{?suse_version}
%debug_package
%endif

%define WITH_CC_OPT $(echo %{optflags} $(pcre2-config --cflags))
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")
%define MODULE_CONFIGURE_ARGS $(echo "--add-dynamic-module=./ngx_brotli/")

%prep
%setup -qcTn %{name}-%{base_version}
tar --strip-components=1 -zxf %{SOURCE0}
tar -zxf %{SOURCE2}



%build

cd %{bdir}

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
	--with-cc-opt="%{WITH_CC_OPT} " \
	--with-ld-opt="%{WITH_LD_OPT} " \
	--with-debug
make %{?_smp_mflags} modules
for so in `find %{bdir}/objs/ -type f -name "*.so"`; do
debugso=`echo $so | sed -e 's|\.so$|-debug.so|'`
mv $so $debugso
done

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
	--with-cc-opt="%{WITH_CC_OPT} " \
	--with-ld-opt="%{WITH_LD_OPT} "
make %{?_smp_mflags} modules

%install
cd %{bdir}
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-brotli
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-brotli/



%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules
for so in `find %{bdir}/objs/ -maxdepth 1 -type f -name "*.so"`; do
%{__install} -m755 $so \
   $RPM_BUILD_ROOT%{_libdir}/nginx/modules/
done

%check
%{__rm} -rf $RPM_BUILD_ROOT/usr/src
cd %{bdir}
grep -v 'usr/src' debugfiles.list > debugfiles.list.new && mv debugfiles.list.new debugfiles.list
cat /dev/null > debugsources.list
%if 0%{?suse_version} >= 1500
cat /dev/null > debugsourcefiles.list
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_libdir}/nginx/modules/*
%dir %{_datadir}/doc/nginx-module-brotli
%{_datadir}/doc/nginx-module-brotli/*


%post
if [ $1 -eq 1 ]; then
cat <<BANNER
----------------------------------------------------------------------

The Brotli dynamic module for nginx has been installed.
To enable this module, add the following to /etc/nginx/nginx.conf
and reload nginx:

    load_module modules/ngx_http_brotli_filter_module.so;
    load_module modules/ngx_http_brotli_static_module.so;

Please refer to the module documentation for further details:
https://github.com/google/ngx_brotli
https://github.com/google/brotli

----------------------------------------------------------------------
BANNER
fi

%changelog
* Sat Jul 23 2022 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.23.1

* Wed Jun 22 2022 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.23.0

* Thu Jan 27 2022 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.6

* Mon Jan  3 2022 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.5

* Tue Nov  9 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.4

* Fri Sep 10 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.3

* Thu Sep  2 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.2

* Thu Jul  7 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.1

* Thu May 27 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.21.0

* Thu Apr 15 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.10

* Wed Mar 31 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.9

* Thu Mar 11 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.8

* Thu Feb 18 2021 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.7

* Tue Dec 22 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.6

* Wed Nov 25 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.5

* Fri Oct 30 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.4

* Thu Oct  1 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.3

* Wed Aug 12 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.2

* Wed Jul  8 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.1

* Wed May 27 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.19.0

* Sat Apr 18 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.10

* Thu Mar  5 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.9

* Thu Jan 23 2020 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.8

* Sat Dec 28 2019 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.7

* Mon Nov 25 2019 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.6

* Wed Oct 23 2019 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.5

* Sun Oct 13 2019 Eugene Wu <kuretru@gmail.com>
- base version updated to 1.17.4
