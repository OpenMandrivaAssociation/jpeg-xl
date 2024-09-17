%bcond_without gdk_pixbuf
%bcond_without gimp
%bcond_without java

%define libname %mklibname jxl
%define threadslibname %mklibname jxl_threads
%define oldlibname %mklibname jxl 0
%define oldthreadslibname %mklibname jxl_threads 0
%define devname %mklibname -d jxl
%define staticname %mklibname -d -s jxl
%define cmsname %mklibname jxl_cms
%define extrasname %mklibname jxl_extras_codec

%define majorminor %(echo %{version} |cut -d. -f1-2)
#define pre 20210521
%define vtag %{?pre:%{majorminor}.x}%{!?pre:%{version}}

Summary:	Library for working with JPEG XL files
Name:		jpeg-xl
Version:	0.11.0
Release:	%{?pre:0.%{pre}.}1
Source0:	https://github.com/libjxl/libjxl/archive/refs/tags/v%{version}/libjxl-%{version}.tar.gz
Source1:	https://github.com/lvandeve/lodepng/archive/master/lodepng.tar.gz
Source2:	https://github.com/webmproject/sjpeg/archive/master/sjpeg.tar.gz
Source3:	https://skia.googlesource.com/skcms/+archive/b25b07b4b07990811de121c0356155b2ba0f4318.tar.gz
Source4:	image-jxl.xml
Patch0:		jpeg-xl-make-helpers-static.patch
Patch1:		libjxl-0.9.0-system-libjpeg-turbo.patch
BuildRequires:	pkgconfig(libbrotlienc)
BuildRequires:	pkgconfig(libbrotlidec)
BuildRequires:	pkgconfig(libhwy) >= 1.0.7
BuildRequires:	pkgconfig(opengl)
BuildRequires:	pkgconfig(glut)
BuildRequires:	cmake ninja
BuildRequires:	doxygen
%if %{with java}
BuildRequires:	jdk-current jre-gui-current
%endif
# For man pages
BuildRequires:	a2x
License:	Apache 2.0

# Not vital, only for transcoding tools
# feel free to disable for bootstrap builds
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(OpenEXR)
BuildRequires:	pkgconfig(libwebp)
BuildRequires:	pkgconfig(libwebpdecoder)
BuildRequires:	pkgconfig(libwebpdemux)
BuildRequires:	pkgconfig(libwebpmux)
BuildRequires:	pkgconfig(libavif)
BuildRequires:	giflib-devel

%if %{with gdk_pixbuf}
BuildRequires:	pkgconfig(gdk-pixbuf-2.0)
BuildRequires:	xdg-utils
%endif
%if %{with gimp}
BuildRequires:	pkgconfig(gimp-2.0)
BuildRequires:	pkgconfig(gimpui-2.0)
%endif

%description
Library for working with JPEG XL files

%package tools
Summary:	Tools for working with JPEG XL files
Requires:	%{libname} = %{EVRD}

%description tools
Tools for working with JPEG XL files

%package -n %{libname}
Summary:	Library for working with JPEG XL files
Group:		System/Libraries
Requires:	%{threadslibname} = %{EVRD}
Requires:	%{name} = %{EVRD}
%rename %{oldlibname}

%description -n %{libname}
Library for working with JPEG XL files

%package -n %{cmsname}
Summary:	CMS library for JPEG XL
Requires:	%{name} = %{EVRD}
Group:		System/Libraries

%description -n %{cmsname}
CMS library for JPEG XL

%package -n %{extrasname}
Summary:	Extra codecs for JPEG XL
Group:		System/Libraries

%description -n %{extrasname}
Extra codecs for JPEG XL

%package -n %{threadslibname}
Summary:	Threading library used by the JPEG XL library
Group:		System/Libraries
%rename %{oldthreadslibname}

%description -n %{threadslibname}
Threading library used by the JPEG XL library

%package -n %{devname}
Summary:	Development files for the JPEG XL library
Requires:	%{libname} = %{EVRD}
Group:		Development/C and C++

%description -n %{devname}
Development files for the JPEG XL library

%package -n %{staticname}
Summary:	Static library for the JPEG XL library
Requires:	%{devname} = %{EVRD}
Group:		Development/C and C++

%description -n %{staticname}
Static library for the JPEG XL library

%package gdk-pixbuf
Summary:	JPEG XL plugin for gdk-pixbuf
Requires:	%{libname} = %{EVRD}
Supplements:	gdk-pixbuf2.0
Group:		Development/C and C++

%description gdk-pixbuf
JPEG XL plugin for gdk-pixbuf

%package gimp
Summary:	GIMP plugin for handling JPEG XL files
Requires:	%{libname} = %{EVRD}
Supplements:	gimp

%description gimp
GIMP plugin for handling JPEG XL files

%package java
Summary:	Java library for handling JPEG XL files
Requires:	%{libname} = %{EVRD}
Group:		Development/Java

%description java
Java library for handling JPEG XL files

%prep
%setup -qn libjxl-%{version}
cd third_party
tar xf %{S:1}
mv lodepng-master lodepng
tar xf %{S:2}
rmdir sjpeg
mv sjpeg-master sjpeg
cd skcms
tar xf %{S:3}
cd ..
cd ..
%autopatch -p1

. %{_sysconfdir}/profile.d/90java.sh

# Debug java detection
sed -i -e 's, QUIET,,g' tools/CMakeLists.txt

# FIXME disabling JPEGXL_ENABLE_BENCHMARK is a workaround
# for a clang 12 crash during linking
%cmake \
	-DJPEGXL_ENABLE_BENCHMARK:BOOL=OFF \
%if %{with gdk_pixbuf} || %{with gimp}
	-DJPEGXL_ENABLE_PLUGINS:BOOL=ON \
%endif
	-G Ninja

%build
export LD_LIBRARY_PATH=$(pwd)/build/lib
%ninja_build -C build

%install
export LD_LIBRARY_PATH=$(pwd)/build/lib
%ninja_install -C build
install -D -m 644 %{S:4} %{buildroot}%{_datadir}/mime/packages/image-jxl.xml

%files
%{_datadir}/mime/packages/image-jxl.xml

%files tools
%{_bindir}/cjxl
%{_bindir}/djxl
%{_bindir}/jxlinfo
%{_mandir}/man1/cjxl.1*
%{_mandir}/man1/djxl.1*

%files -n %{libname}
%{_libdir}/libjxl.so.0*

%files -n %{cmsname}
%{_libdir}/libjxl_cms.so.0*

%files -n %{extrasname}
%{_libdir}/libjxl_extras_codec.so.0*

%files -n %{threadslibname}
%{_libdir}/libjxl_threads.so.0*

%files -n %{devname}
%{_includedir}/jxl
%{_libdir}/libjxl.so
%{_libdir}/libjxl_cms.so
%{_libdir}/libjxl_extras_codec.so
%{_libdir}/libjxl_threads.so
%{_libdir}/pkgconfig/libjxl.pc
%{_libdir}/pkgconfig/libjxl_cms.pc
%{_libdir}/pkgconfig/libjxl_threads.pc

%if %{with gdk_pixbuf}
%files gdk-pixbuf
%{_libdir}/gdk-pixbuf-2.0/*/loaders/libpixbufloader-jxl.so
%{_datadir}/thumbnailers/jxl.thumbnailer
%endif

%if %{with gimp}
%files gimp
%{_libdir}/gimp/*/plug-ins/file-jxl
%endif

%if %{with java}
%files java
%{_libdir}/libjxl_jni.so
%{_libdir}/org.jpeg.jpegxl.jar
%endif
