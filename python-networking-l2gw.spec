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
BuildRequires:  python2-hacking
BuildRequires:  python2-oslotest
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools
BuildRequires:  python2-subunit
BuildRequires:  python2-testrepository
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools
BuildRequires:  python2-devel
BuildRequires:  systemd-units

%description
%{common_desc}

%package -n     python2-%{pypi_name}
Summary:        API's and implementations to support L2 Gateways in Neutron
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires:       python2-pbr >= 2.0.0
Requires:       python2-babel >= 2.3.4
Requires:       python-neutron-lib >= 1.13.0
Requires:       python2-neutronclient >= 6.3.0
Requires:       python-neutron
Requires:       openstack-neutron-common
Requires:       python2-ovsdbapp >= 0.8.0

%description -n python2-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:    networking-l2gw documentation

BuildRequires:  python2-sphinx
BuildRequires:  python2-oslo-sphinx

%description doc
Documentation for networking-l2gw
%endif

%package tests
Summary:    networking-l2gw tests
Requires:   python-%{pypi_name} = %{epoch}:%{version}-%{release}
Requires:   python2-subunit >= 0.0.18
Requires:   python2-oslotest >= 1.10.0
Requires:   python2-testrepository >= 0.0.18
Requires:   python2-testresources >= 0.2.4
Requires:   python2-testscenarios >= 0.4
Requires:   python2-testtools >= 1.4.0
Requires:   python2-mock >= 2.0.0

%description tests
Networking-l2gw set of tests

%package -n openstack-%{servicename}-agent
Summary:    Neutron L2 Gateway Agent
Requires:   python-%{pypi_name} = %{epoch}:%{version}-%{release}

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
%py2_build
%if 0%{?with_doc}
# generate html docs
%{__python2} setup.py build_sphinx -b html
# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%py2_install

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

%files -n python2-%{pypi_name}
%license LICENSE
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gw_plugin.ini
%{_datadir}/neutron/server/l2gw_plugin.conf
%dir %{_sysconfdir}/neutron/conf.d/%{servicename}-agent
%exclude %{python2_sitelib}/%{sname}/tests

%if 0%{?with_doc}
%files -n %{name}-doc
%license LICENSE
%doc README.rst
%endif

%files -n %{name}-tests
%license LICENSE
%{python2_sitelib}/%{sname}/tests
%{python2_sitelib}/%{sname}/tests/__init__.py

%files -n openstack-%{servicename}-agent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gateway_agent.ini
%{_unitdir}/%{servicename}-agent.service
%{_bindir}/neutron-l2gateway-agent

%changelog
