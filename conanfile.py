from conans import ConanFile, CMake, tools
import os

class LibrtmpConan(ConanFile):
    name = "librtmp"
    version = "2.4_p20151223"
    description = "RTMPDump Real-Time Messaging Protocol API"
    url = "https://github.com/conan-multimedia/librtmp"
    wiki = 'http://rtmpdump.mplayerhq.hu/librtmp.3.html'
    license = "LGPLv2_1"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "gnutls/3.5.18@conanos/dev","nettle/3.4@conanos/dev","gmp/6.1.2@conanos/dev"
    source_subfolder = "source_subfolder"
    
    def source(self):
        tools.get("https://gstreamer.freedesktop.org/data/src/mirror/rtmpdump-2.4_p20151223.tar.gz")
        extracted_dir = "rtmpdump-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'C_INCLUDE_PATH' : "%s/include:%s/include:%s/include"
                %(self.deps_cpp_info["gnutls"].rootpath,self.deps_cpp_info["nettle"].rootpath,
                self.deps_cpp_info["gmp"].rootpath,),
                'LIBRARY_PATH' : "%s/lib:%s/lib:%s/lib"
                %(self.deps_cpp_info["gnutls"].rootpath,self.deps_cpp_info["nettle"].rootpath,
                self.deps_cpp_info["gmp"].rootpath),
                }):
                
                self.run('make SYS=posix prefix=%s/builddir CRYPTO=GNUTLS'%(os.getcwd()))
                self.run('make install SYS=posix prefix=%s/builddir CRYPTO=GNUTLS'%(os.getcwd()))
                

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

