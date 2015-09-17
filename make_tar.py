# -*- encoding: utf-8 -*-

'''
liyan30 @ 2015-04-26 13:41
For making tar file of ACM problems
Only used in git bash
'''

import os
import sys
import os.path
import shutil

def ensure_dir(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def system_warpper(command):
    print "+++", command
    os.system(command)

parent_dir = 'astar'
problem_names = ['balance', 'flip', 'magic', 'remove', 'starchaser', 'tough', 'ultra', 'way']
target_file_suffix = ['.cpp', '_gen.py']
target_file_list = [i + j for i in problem_names for j in target_file_suffix]

def process_file(arg, dirname, names):
    # print dirname
    if parent_dir in dirname:
        return
    for name in names:
        # print name
        if name in target_file_list:
        # if '-check' in name and 'exe' not in name:
            src_path = dirname + '/' + name
            dst_path = parent_dir + '/' + dirname + '/' + name
            ensure_dir(parent_dir + '/' + dirname)
            # print src_path, dst_path
            sys.stderr.write('Copy file %s to %s...\n' % (src_path, dst_path))
            shutil.copyfile(src_path, dst_path)

def main():
    # ensure_dir(parent_dir)
    system_warpper('rm -rf %s' % (parent_dir, ))
    # for problem_name in problem_names:
    #     ensure_dir(parent_dir + '/' + problem_name)
    os.path.walk('.', process_file, None)
    system_warpper('tar -czvf %s %s' % (parent_dir + '.tar.gz', parent_dir))

if __name__ == '__main__':
    main()
