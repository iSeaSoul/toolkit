import os
import sys

def del_suffix_file(arg, dirname, names):
    for name in names:
        if name[-len(arg):] == arg:
            sys.stderr.write('Delete file %s...\n' % (dirname + '\\' + name, ))
            os.remove(dirname + '\\' + name)

def main():
    suffix = 'dump'
    if len(sys.argv) > 1:
        suffix = sys.argv[1]
    
    os.path.walk('.', del_suffix_file, suffix)

if __name__ == '__main__':
    main()
