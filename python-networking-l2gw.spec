%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
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
Source0:        http://tarballs.opendev.org/x/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        %{servicename}-agent.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.opendev.org/x/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif
BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires:  git-core
BuildRequires:  openstack-macros
BuildRequires:  python3-hacking
BuildRequires:  python3-oslotest
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools
BuildRequires:  python3-subunit
BuildRequires:  python3-testrepository
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools
BuildRequires:  python3-devel
BuildRequires:  systemd-units

%description
%{common_desc}

%package -n     python3-%{pypi_name}
Summary:        API's and implementations to support L2 Gateways in Neutron
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       python3-pbr >= 4.0.0
Requires:       python3-neutron-lib >= 3.1.0
Requires:       python3-neutronclient >= 7.8.0
Requires:       python3-neutron >= 16.0.0
Requires:       openstack-neutron-common >= 1:21.0.0
Requires:       python3-ovsdbapp >= 1.16.0

%description -n python3-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:    networking-l2gw documentation

BuildRequires:  python3-sphinx
BuildRequires:  python3-openstackdocstheme

%description doc
Documentation for networking-l2gw
%endif

%package -n python3-%{pypi_name}-tests
Summary:    networking-l2gw tests
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:   python3-%{pypi_name} = %{epoch}:%{version}-%{release}
Requires:   python3-subunit >= 0.0.18
Requires:   python3-oslotest >= 1.10.0
Requires:   python3-testrepository >= 0.0.18
Requires:   python3-testresources >= 0.2.4
Requires:   python3-testscenarios >= 0.4
Requires:   python3-testtools >= 1.4.0
Requires:   python3-mock >= 2.0.0

%description -n python3-%{pypi_name}-tests
Networking-l2gw set of tests

%package -n openstack-%{servicename}-agent
Summary:    Neutron L2 Gateway Agent

Requires:   python3-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n openstack-%{servicename}-agent
Agent that enables L2 Gateway functionality

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
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
%{py3_build}
%if 0%{?with_doc}
# generate html docs
sphinx-build-3 -W -b html doc/source doc/build/html
# remove the sphinx-build-3 leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

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

%files -n python3-%{pypi_name}
%license LICENSE
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.egg-info
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gw_plugin.ini
%{_datadir}/neutron/server/l2gw_plugin.conf
%dir %{_sysconfdir}/neutron/conf.d/%{servicename}-agent
%exclude %{python3_sitelib}/%{sname}/tests

%if 0%{?with_doc}
%files -n python-%{pypi_name}-doc
%license LICENSE
%doc README.rst
%endif

%files -n python3-%{pypi_name}-tests
%license LICENSE
%{python3_sitelib}/%{sname}/tests
%{python3_sitelib}/%{sname}/tests/__init__.py

%files -n openstack-%{servicename}-agent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l2gateway_agent.ini
%{_unitdir}/%{servicename}-agent.service
%{_bindir}/neutron-l2gateway-agent

%changelog
