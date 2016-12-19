%global pypi_name networking-l2gw
%global sname networking_l2gw
%global servicename neutron-l2gw
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pypi_name}
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
BuildRequires:  python-tempest-lib
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
BuildRequires:  python2-devel
BuildRequires:  python-sphinx
BuildRequires:  systemd-units

%description
This project proposes a Neutron API extension that can be used to express and
manage L2 Gateway components. In the simplest terms L2 Gateways are meant to
bridge two or more networks together to make them look at a single L2 broadcast
domain.

%package -n     python2-%{pypi_name}
Summary:        API's and implementations to support L2 Gateways in Neutron
%{?python_provide:%python_provide python2-%{pypi_name}}
 
Requires:       python-pbr >= 1.6
Requires:       python-babel >= 1.3
Requires:       python-neutron-lib >= 0.0.3
Requires:       python-neutronclient >= 4.1.1
Requires:       python-setuptools

%description -n python2-%{pypi_name}
This project proposes a Neutron API extension that can be used to express and
manage L2 Gateway components. In the simplest terms L2 Gateways are meant to
bridge two or more networks together to make them look at a single L2 broadcast
domain.

%package -n python-%{pypi_name}-doc
Summary:    networking-l2gw documentation
%description -n python-%{pypi_name}-doc
Documentation for networking-l2gw

%package -n python-%{pypi_name}-tests
Summary:    networking-l2gw tests
Requires:   python-%{pypi_name} = %{version}-%{release}

%description -n python-%{pypi_name}-tests
Networking-l2gw set of tests 

%prep
%autosetup -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py2_build
# generate html docs
# TODO: the doc generation is commented until python-sphinxcontrib-* packages
# are included in CBS. This needs to be fixed.
%{__python2} setup.py build_sphinx
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%py2_install

mkdir -p %{buildroot}%{_sysconfdir}/neutron/
mv %{buildroot}/usr/etc/neutron/l2gateway_agent.ini %{buildroot}%{_sysconfdir}/neutron/
mv %{buildroot}/usr/etc/neutron/l2gw_plugin.ini %{buildroot}%{_sysconfdir}/neutron/

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{servicename}-agent.service

%post
%systemd_post %{servicename}-agent.service

%preun
%systemd_preun %{servicename}-agent.service

%postun
%systemd_postun_with_restart %{servicename}-agent.service

%files -n python2-%{pypi_name}
%license LICENSE
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%{_unitdir}/%{servicename}-agent.service
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gateway_agent.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gw_plugin.ini
%config(noreplace) %attr(0640, root, neutron) %{_bindir}/neutron-l2gateway-agent
%exclude %{python2_sitelib}/%{sname}/tests                                                                                                                                                                

%files -n python-%{pypi_name}-doc
%license LICENSE
%doc doc/source/readme.rst networking_l2gw/services/l2gateway/agent/ovsdb/README.rst README.rst devstack/README.rst contrib/README_install_and_config_l2gateway_plugin.rst contrib/README_install_l2gateway_agent.rst

%files -n python-%{pypi_name}-tests
%license LICENSE
%{python2_sitelib}/%{sname}/tests

%changelog
* Tue Dec 13 2016 Ricardo Noriega <rnoriega@redhat.com> - 2016.1.0-1
- Initial package.
