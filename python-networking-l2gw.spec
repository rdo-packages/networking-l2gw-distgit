# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global pypi_name networking-l2gw
%global sname networking_l2gw
%global servicename neutron-l2gw
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

%global common_desc \
This project proposes a Neutron API extension that can be used to express and \
manage L2 Gateway components. In the simplest terms L2 Gateways are meant to \
bridge two or more networks together to make them look as a single L2 broadcast \
domain.

Name:           python-%{pypi_name}
Epoch:          1
Version:        XXX
Release:        XXX
Summary:        API's and implementations to support L2 Gateways in Neutron

License:        ASL 2.0
URL:            https://docs.openstack.org/developer/networking-l2gw/
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        %{servicename}-agent.service
BuildArch:      noarch

BuildRequires:  git
BuildRequires:  openstack-macros
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-oslotest
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-subunit
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-testtools
BuildRequires:  python%{pyver}-devel
BuildRequires:  systemd-units

%description
%{common_desc}

%package -n     python%{pyver}-%{pypi_name}
Summary:        API's and implementations to support L2 Gateways in Neutron
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

Requires:       python%{pyver}-pbr >= 2.0.0
Requires:       python%{pyver}-babel >= 2.3.4
Requires:       python%{pyver}-neutron-lib >= 1.18.0
Requires:       python%{pyver}-neutronclient >= 6.7.0
Requires:       python%{pyver}-neutron >= 12.0.0
Requires:       openstack-neutron-common
Requires:       python%{pyver}-ovsdbapp >= 0.10.0

%description -n python%{pyver}-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:    networking-l2gw documentation
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-oslo-sphinx

%description doc
Documentation for networking-l2gw
%endif

%package -n python%{pyver}-%{pypi_name}-tests
Summary:    networking-l2gw tests
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

Requires:   python%{pyver}-%{pypi_name} = %{epoch}:%{version}-%{release}
Requires:   python%{pyver}-subunit >= 0.0.18
Requires:   python%{pyver}-oslotest >= 1.10.0
Requires:   python%{pyver}-testrepository >= 0.0.18
Requires:   python%{pyver}-testresources >= 0.2.4
Requires:   python%{pyver}-testscenarios >= 0.4
Requires:   python%{pyver}-testtools >= 1.4.0
Requires:   python%{pyver}-mock >= 2.0.0

%description python%{pyver}-%{pypi_name}-tests
Networking-l2gw set of tests

%package -n openstack-%{servicename}-agent
Summary:    Neutron L2 Gateway Agent
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

Requires:   python%{pyver}-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n openstack-%{servicename}-agent
Agent that enables L2 Gateway functionality

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# remove requirements
%py_req_cleanup
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

# Remove tempest plugin entrypoint as a workaround
sed -i '/tempest/d' setup.cfg
rm -rf networking_l2gw/tests/tempest
rm -rf networking_l2gw/tests/api

%build
%{pyver_build}
%if 0%{?with_doc}
# generate html docs
%{pyver_bin} setup.py build_sphinx -b html
# remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

mkdir -p %{buildroot}%{_sysconfdir}/neutron/conf.d/neutron-l2gw-agent
mv %{buildroot}/usr/etc/neutron/*.ini %{buildroot}%{_sysconfdir}/neutron/

# Make sure neutron-server loads new configuration file
mkdir -p %{buildroot}/%{_datadir}/neutron/server
ln -s %{_sysconfdir}/neutron/l2gw_plugin.ini %{buildroot}%{_datadir}/neutron/server/l2gw_plugin.conf

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{servicename}-agent.service

%post -n openstack-%{servicename}-agent
%systemd_post %{servicename}-agent.service

%preun -n openstack-%{servicename}-agent
%systemd_preun %{servicename}-agent.service

%postun -n openstack-%{servicename}-agent
%systemd_postun_with_restart %{servicename}-agent.service

%files -n python%{pyver}-%{pypi_name}
%license LICENSE
%{pyver_sitelib}/%{sname}
%{pyver_sitelib}/%{sname}-*.egg-info
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gw_plugin.ini
%{_datadir}/neutron/server/l2gw_plugin.conf
%dir %{_sysconfdir}/neutron/conf.d/%{servicename}-agent
%exclude %{pyver_sitelib}/%{sname}/tests

%if 0%{?with_doc}
%files -n python-%{pypi_name}-doc
%license LICENSE
%doc README.rst
%endif

%files -n %{name}-tests
%license LICENSE
%{pyver_sitelib}/%{sname}/tests
%{pyver_sitelib}/%{sname}/tests/__init__.py

%files -n openstack-%{servicename}-agent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gateway_agent.ini
%{_unitdir}/%{servicename}-agent.service
%{_bindir}/neutron-l2gateway-agent

%changelog
