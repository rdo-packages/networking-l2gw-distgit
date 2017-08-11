%global pypi_name networking-l2gw
%global sname networking_l2gw
%global servicename neutron-l2gw
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

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
BuildRequires:  python-hacking
BuildRequires:  python-oslotest
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-subunit
BuildRequires:  python-tempest
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
BuildRequires:  python2-devel
BuildRequires:  systemd-units

%description
This project proposes a Neutron API extension that can be used to express and
manage L2 Gateway components. In the simplest terms L2 Gateways are meant to
bridge two or more networks together to make them look as a single L2 broadcast
domain.

%package -n     python2-%{pypi_name}
Summary:        API's and implementations to support L2 Gateways in Neutron
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires:       python-pbr >= 1.6
Requires:       python-babel >= 1.3
Requires:       python-neutron-lib >= 0.0.3
Requires:       python-neutronclient >= 4.1.1
Requires:       python-neutron
Requires:       python-setuptools
Requires:       openstack-neutron-common

%description -n python2-%{pypi_name}
This project proposes a Neutron API extension that can be used to express and
manage L2 Gateway components. In the simplest terms L2 Gateways are meant to
bridge two or more networks together to make them look at a single L2 broadcast
domain.

%if 0%{?with_doc}
%package doc
Summary:    networking-l2gw documentation

BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx

%description doc
Documentation for networking-l2gw
%endif

%package tests
Summary:    networking-l2gw tests
Requires:   python-%{pypi_name} = %{epoch}:%{version}-%{release}
Requires:   python-subunit >= 0.0.18
Requires:   python-oslotest >= 1.10.0
Requires:   python-testrepository >= 0.0.18
Requires:   python-testresources >= 0.2.4
Requires:   python-testscenarios >= 0.4
Requires:   python-testtools >= 1.4.0
Requires:   python-mock >= 2.0.0

%description tests
Networking-l2gw set of tests

%package -n %{name}-tests-tempest
Summary:    %{sname} Tempest Plugin

Requires:   python-%{pypi_name} = %{epoch}:%{version}-%{release}

Requires:   python-neutron-tests
Requires:   python-tempest >= 14.0.0

%description -n %{name}-tests-tempest
It contains tempest plugin for %{name}.

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

%build
%py2_build
%if 0%{?with_doc}
# generate html docs
%{__python2} setup.py build_sphinx
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
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

%py2_entrypoint %{sname} %{pypi_name}

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
%{python2_sitelib}/%{sname}_tests.egg-info
%exclude %{python2_sitelib}/%{sname}/tests/tempest
%exclude %{python2_sitelib}/%{sname}/tests/api

%files -n openstack-%{servicename}-agent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gateway_agent.ini
%{_unitdir}/%{servicename}-agent.service
%{_bindir}/neutron-l2gateway-agent

%files -n %{name}-tests-tempest
%{python2_sitelib}/%{sname}_tests.egg-info
%{python2_sitelib}/%{sname}/tests/__init__.py
%{python2_sitelib}/%{sname}/tests/tempest
%{python2_sitelib}/%{sname}/tests/api

%changelog
