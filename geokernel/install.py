import json
import os
import sys
import argparse
import shutil


from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory

kernel_json = {
    "argv": [sys.executable, "-m", "geokernel", "-f", "{connection_file}"],
    "display_name": "Geo",
    "codemirror_mode": "geo",
    "language": "geo"
}


def install_my_kernel_spec(user=True, prefix=None):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755)  # Starts off as 700, not user readable
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)

        print('Installing IPython kernel spec')
        KernelSpecManager().install_kernel_spec(td, 'geo', user=user, replace=True, prefix=prefix)


def setup_config(user=False, prefix=None, port=9090, ip='127.0.0.1'):
    destination = KernelSpecManager()._get_destination_dir('geo', user=user, prefix=prefix)
    print(destination)
    print(os.path.isdir(destination))
    if os.path.isdir(destination):
        print(destination + '/config.txt')
        with open(os.path.join(destination, 'config.txt'), 'w') as f:
            f.write('port=' + str(port) + '\n')
            f.write('ip=' + ip + '\n')
        cmd_path = os.path.dirname(os.path.realpath(__file__))
        shutil.copyfile(os.path.join(cmd_path, 'cmd.json'), os.path.join(destination, 'cmd.json'))


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Install KernelSpec for Geo Kernel'
    )

    parser.add_argument('--port', default=9090)
    parser.add_argument('--ip', default='127.0.0.1')

    prefix_locations = parser.add_mutually_exclusive_group()

    prefix_locations.add_argument(
        '--user',
        help='Install KernelSpec in user homedirectory',
        action='store_true'
    )
    prefix_locations.add_argument(
        '--sys-prefix',
        help='Install KernelSpec in sys.prefix. Useful in conda / virtualenv',
        action='store_true',
        dest='sys_prefix'
    )
    prefix_locations.add_argument(
        '--prefix',
        help='Install KernelSpec in this prefix',
        default=None
    )

    args = parser.parse_args(argv)

    user = False
    prefix = None
    port = args.port
    ip = args.ip
    if args.sys_prefix:
        prefix = sys.prefix
    elif args.prefix:
        prefix = args.prefix
    elif args.user or not _is_root():
        user = True

    install_my_kernel_spec(user=user, prefix=prefix)
    setup_config(user=user, prefix=prefix, port=port, ip=ip)


if __name__ == '__main__':
    main()
