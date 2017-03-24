%global pypi_name networking-l2gw
%global sname networking_l2gw
%global servicename neutron-l2gw
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pypi_name}
Epoch:          1
Version:        XXX
Release:        XXX
Summary:        API's and implementations to support L2 Gateways in Neutron

License:        ASL 2.0
URL:            http://www.openstack.org/
Source0:        https://files.pythonhosted.org/packages/source/n/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        %{servicename}-agent.service
BuildArch:      noarch

BuildRequires:  python-coverage
BuildRequires:  python-hacking
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-oslotest
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-subunit
BuildRequires:  python-tempest
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
BuildRequires:  python2-devel
BuildRequires:  python-sphinx
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

%package doc
Summary:    networking-l2gw documentation
%description doc
Documentation for networking-l2gw

%package tests
Summary:    networking-l2gw tests
Requires:   python-%{pypi_name} = %{epoch}:%{version}-%{release}
Requires:   python-hacking >= 0.9.2
Requires:   python-coverage
Requires:   python-neutron-tests
Requires:   python-subunit >= 0.0.18
Requires:   python-sphinx >= 1.2.1
Requires:   python-oslo-sphinx >= 4.7.0
Requires:   python-oslotest >= 1.10.0
Requires:   python-testrepository >= 0.0.18
Requires:   python-testresources >= 0.2.4
Requires:   python-testscenarios >= 0.4
Requires:   python-testtools >= 1.4.0
Requires:   python-tempest >= 14.0.0
Requires:   mock

%description tests
Networking-l2gw set of tests

%package -n openstack-%{servicename}-agent
Summary:    Neutron L2 Gateway Agent
Requires:   python-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n openstack-%{servicename}-agent
Agent that enables L2 Gateway functionality

%prep
%autosetup -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py2_build
# generate html docs
%{__python2} setup.py build_sphinx
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

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

%files -n python-%{pypi_name}-doc
%license LICENSE
%doc README.rst

%files -n python-%{pypi_name}-tests
%license LICENSE
%{python2_sitelib}/%{sname}/tests

%files -n openstack-%{servicename}-agent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gateway_agent.ini
%{_unitdir}/%{servicename}-agent.service
%{_bindir}/neutron-l2gateway-agent

%changelog
* Tue Dec 13 2016 Ricardo Noriega <rnoriega@redhat.com> - 2016.1.0-1
- Initial package.
