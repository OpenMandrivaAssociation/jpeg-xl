%bcond_without gdk_pixbuf
%bcond_without gimp

%define libname %mklibname jxl 0
%define threadslibname %mklibname jxl_threads 0
%define devname %mklibname -d jxl
%define staticname %mklibname -d -s jxl

Summary:	Library for working with JPEG XL files
Name:		jpeg-xl
Version:	0.3.6
Release:	1
Source0:	https://gitlab.com/wg1/jpeg-xl/-/archive/v%{version}/jpeg-xl-v%{version}.tar.bz2
Source1:	https://github.com/lvandeve/lodepng/archive/master/lodepng.tar.gz
Source2:	https://github.com/webmproject/sjpeg/archive/master/sjpeg.tar.gz
Source3:	https://skia.googlesource.com/skcms/+archive/64374756e03700d649f897dbd98c95e78c30c7da.tar.gz
Patch0:		jpeg-xl-make-helpers-static.patch
BuildRequires:	pkgconfig(libbrotlienc)
BuildRequires:	pkgconfig(libbrotlidec)
BuildRequires:	pkgconfig(libhwy)
BuildRequires:	pkgconfig(opengl)
BuildRequires:	pkgconfig(glut)
BuildRequires:	cmake ninja
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
Requires:	%{threadslibname} = %{EVRD}
Requires:	%{name} = %{EVRD}

%description -n %{libname}
Library for working with JPEG XL files

%package -n %{threadslibname}
Summary:	Threading library used by the JPEG XL library

%description -n %{threadslibname}
Threading library used by the JPEG XL library

%package -n %{devname}
Summary:	Development files for the JPEG XL library
Requires:	%{libname} = %{EVRD}

%description -n %{devname}
Development files for the JPEG XL library

%package -n %{staticname}
Summary:	Static library for the JPEG XL library
Requires:	%{devname} = %{EVRD}

%description -n %{staticname}
Static library for the JPEG XL library

%package gdk-pixbuf
Summary:	JPEG XL plugin for gdk-pixbuf
Requires:	%{libname} = %{EVRD}
Supplements:	gdk-pixbuf2.0

%description gdk-pixbuf
JPEG XL plugin for gdk-pixbuf

%package gimp
Summary:	GIMP plugin for handling JPEG XL files
Requires:	%{libname} = %{EVRD}
Supplements:	gimp

%description gimp
GIMP plugin for handling JPEG XL files

%prep
%setup -n %{name}-v%{version}
cd third_party
tar xf %{S:1}
rmdir lodepng
mv lodepng-master lodepng
tar xf %{S:2}
rmdir sjpeg
mv sjpeg-master sjpeg
cd skcms
tar xf %{S:3}
cd ..
cd ..
%autopatch -p1

# FIXME disabling JPEGXL_ENABLE_BENCHMARK is a workaround
# for a clang 12 crash during linking
%cmake \
	-DJPEGXL_ENABLE_BENCHMARK:BOOL=OFF \
%if %{with gdk_pixbuf} || %{with gimp}
	-DJPEGXL_ENABLE_PLUGINS:BOOL=ON \
%endif
	-G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build

%files
%{_datadir}/mime/packages/image-jxl.xml

%files tools
%{_bindir}/cjxl
%{_bindir}/djxl

%files -n %{libname}
%{_libdir}/libjxl.so.0*

%files -n %{threadslibname}
%{_libdir}/libjxl_threads.so.0*

%files -n %{devname}
%{_includedir}/jxl
%{_libdir}/libjxl.so
%{_libdir}/libjxl_threads.so
%{_libdir}/pkgconfig/libjxl.pc
%{_libdir}/pkgconfig/libjxl_threads.pc

%files -n %{staticname}
%{_libdir}/libjxl.a
%{_libdir}/libjxl_dec.a
%{_libdir}/libjxl_threads.a

%if %{with gdk_pixbuf}
%files gdk-pixbuf
%{_libdir}/gdk-pixbuf-2.0/*/loaders/libpixbufloader-jxl.so
%{_datadir}/thumbnailers/jxl.thumbnailer
%endif

%if %{with gimp}
%files gimp
%{_libdir}/gimp/*/plug-ins/file-jxl
%endif
