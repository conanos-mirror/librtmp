from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os

class LibrtmpConan(ConanFile):
    name = "librtmp"
    version = "2.4.r512-1"
    description = "RTMPDump Real-Time Messaging Protocol API, a toolkit for RTMP streams"
    url = "https://github.com/conanos/librtmp"
    homepage = "http://rtmpdump.mplayerhq.hu/"
    license = "GPL-2.0"
    exports = ["COPYING"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }
    #requires = "gnutls/3.5.18@conanos/dev","nettle/3.4@conanos/dev","gmp/6.1.2@conanos/dev"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("gnutls/3.5.19-2@conanos/stable")
        self.requires.add("nettle/3.4.1@conanos/stable")
        self.requires.add("gmp/6.1.2-5@conanos/stable")

    def build_requirements(self):
        self.build_requires("zlib/1.2.11@conanos/stable")

    def source(self):
        url_='https://github.com/ShiftMediaProject/rtmpdump/archive/v{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        extracted_dir = "rtmpdump-" + self.version
        os.rename(extracted_dir, self._source_subfolder)


    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    with tools.environment_append({
        #        'C_INCLUDE_PATH' : "%s/include:%s/include:%s/include"
        #        %(self.deps_cpp_info["gnutls"].rootpath,self.deps_cpp_info["nettle"].rootpath,
        #        self.deps_cpp_info["gmp"].rootpath,),
        #        'LIBRARY_PATH' : "%s/lib:%s/lib:%s/lib"
        #        %(self.deps_cpp_info["gnutls"].rootpath,self.deps_cpp_info["nettle"].rootpath,
        #        self.deps_cpp_info["gmp"].rootpath),
        #        }):
        #        
        #        self.run('make SYS=posix prefix=%s/builddir CRYPTO=GNUTLS'%(os.getcwd()))
        #        self.run('make install SYS=posix prefix=%s/builddir CRYPTO=GNUTLS'%(os.getcwd()))

        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                replacements = {
                    "zlibd.lib" : "zlib.lib"
                }
                for s, r in replacements.items():
                    tools.replace_in_file("librtmp.vcxproj",s,r)

                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("librtmp.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'},build_type=build_type)

    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            rplatform = platforms.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            if self.options.shared:
                for i in ["lib","bin"]:
                    self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

