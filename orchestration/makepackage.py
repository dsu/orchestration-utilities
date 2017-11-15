import os
import os.path
import re
import shutil
import time
from datetime import datetime as dt, timedelta
from distutils import dir_util
from common.java import get_class_version
from common.operations import Operation


class MakePackage(Operation):
    '''This clas prepares files to upadate an applicatoin.'''
    def __init__(self, args={}):
        print('MakePackage {} '.format(args))
        self.args = args
        self.jversion = str(args.get("jversion", "1.6"))
        self.dir_src = args.get("dir_src")
        self.compress = True
        self.dir_dst = args.get("dir_dst");
        self.arch_file_dst = args.get("arch_file_dst", os.path.join(os.getcwd(), "paczka"));

        dir_exclude = args.get("dir_exclude", "");
        self.dir_exclude_regexp = re.compile(dir_exclude)

        hours_old_max = int(args.get("hours_old_max", 8))
        self.newerThan = dt.now() - timedelta(hours=hours_old_max)

    def execute(self):
        skipped = 0
        copied = 0
        bk_dir = self.dir_dst + "_bk"

        if  os.path.exists(self.dir_dst):
            if  not os.path.exists(bk_dir):
                os.makedirs(bk_dir)
            #shutil.copytree(dir_dst, bk_dir)
            dir_util.copy_tree(self.dir_dst, bk_dir)
            shutil.rmtree(self.dir_dst)
            print(' {} moved '.format(self.dir_dst))

        for dirName, subdirList, fileList in os.walk(self.dir_src):
            print('Found directory: %s' % dirName)
            for w in fileList:
                #print('\t%s' % w)
                if not w.endswith(('.temp', '.log')):
                    pathname = os.path.join(dirName, w)
                    file_mod_dt = dt.fromtimestamp(os.stat(pathname).st_mtime)
                    if file_mod_dt  > self.newerThan:
                        if self.dir_exclude_regexp.match(pathname):
                            self.log("exclude {} ",pathname)
                            continue


                        if self.jversion and pathname.endswith(('.class')):
                            ver = str(get_class_version(pathname))
                            if ver != self.jversion:
                                 raise Exception(' {} is not valid {} class file ({})!'.format(pathname, self.jversion,ver))
                        rel = os.path.relpath(pathname,self.dir_src)
                        new_path = os.path.join(self.dir_dst, rel)
                        sep = os.sep
                        new_dir = sep.join(new_path.split(sep)[:-1])
                        if not os.path.exists(new_dir):
                            self.log("create dir {}" , new_dir)
                            os.makedirs(new_dir)
                        shutil.copy2(pathname, new_path)
                        info = "{}. FILE  {}  modified {}  copied to {}. \n".format(copied,w, file_mod_dt,new_path)
                        copied = copied+1;
                    else:
                        skipped = skipped+1

        print("{} files skipped, {} files copied ".format(skipped,copied))
        print(time.asctime( time.localtime(time.time()) ))
        if copied > 0:
            print("archiving {} -> {} ...".format(self.dir_dst,self.arch_file_dst))
            #“zip”, “tar”, “bztar” or “gztar”
            res = shutil.make_archive(self.arch_file_dst, 'gztar', self.dir_dst)
            print("archived {}".format(res))
            self.add_product("package_archive_path",res)
            self._status = self.EXIT_SUCCESS
        else:
            self._status = self.EXIT_FAILURE
            self.log('No modifications!')


