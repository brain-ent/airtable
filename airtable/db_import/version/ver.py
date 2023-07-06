# Do not change names of vars with VER_ and BUILD_ prefixes,
# because they are used by version_update.sh
VER_MAJOR = '2'
VER_MINOR = '0'
VER_PATCH = '0'
# Use BUILD_DATE and BUILD_NUMBER carefully,
# because they will be replaced by the bash script version_update.sh
BUILD_NUMBER = 'number_undefined'
BUILD_DATE = 'date_undefined'


def get_version() -> str:
    return f'{VER_MAJOR}.{VER_MINOR}.{VER_PATCH}.{BUILD_NUMBER}'


def get_build_info() -> str:
    return f'{get_version()}, build date {BUILD_DATE}'


def print_build_info():
    build_info = get_build_info()
    line = '=' * len(build_info)
    print(line)
    print('Current version and build date are:')
    print(build_info)
    print(line)
    if 'undefined' in build_info:
        print('Warning! This version is a direct clone of a git repository')
